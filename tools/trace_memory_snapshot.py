# tools/trace_memory_snapshot.py
# Snapshot wrapper for CLI/reflex test runs.
# - Path injection first (IronRoot), no __future__ import in runnable scripts
# - Phase lock, dual logging, run_id generation
# - Pre/Post snapshots, diffs, audit line, DB index
# - UTF-8 JSON; forward slashes; DB path from core.sqlite_bootstrap

from boot.boot_path_initializer import inject_paths
inject_paths()

import argparse
import importlib
import json
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from core.phase_control import ensure_phase, REQUIRED_PHASE
from core.sqlite_bootstrap import DB_PATH
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event
from core.snapshot_manager import (
    take_snapshot,
    compare_snapshots,
    write_audit_line,
    index_snapshot,
)

def _new_run_id() -> str:
    return str(uuid.uuid4())

def _resolve_callable(module_path: Optional[str]) -> Optional[Any]:
    if not module_path:
        return None
    mod = importlib.import_module(module_path)
    fn = getattr(mod, "run_cli", None) or getattr(mod, "run", None)
    if not callable(fn):
        raise RuntimeError(f"No callable run_cli/run in module: {module_path}")
    return fn

def run_cli() -> None:
    ensure_phase()

    parser = argparse.ArgumentParser(
        description="Trace↔Memory snapshot wrapper",
        allow_abbrev=False,
    )
    parser.add_argument(
        "--module", "-m",
        help="Optional module to execute (e.g., reflexes.reflex_core.reflex_trace_ping). Calls run_cli() or run().",
        default=None,
    )
    parser.add_argument(
        "--args",
        help='Optional JSON for target args, e.g. \'{"k":"v"}\'.',
        default=None,
    )
    parser.add_argument(
        "--snapshot-mode",
        choices=["off", "light", "heavy"],
        default="heavy",
        help="Snapshot strategy; heavy recommended for tests.",
    )
    args = parser.parse_args()

    run_id = _new_run_id()
    mode = args.snapshot_mode
    target_args: Dict[str, Any] = {}
    if args.args:
        try:
            target_args = json.loads(args.args)
        except Exception:
            raise RuntimeError("--args must be valid JSON (e.g., '{\"k\": \"v\"}')")

    tool = Path(__file__).as_posix()

    # Pre snapshot (if enabled)
    pre_meta = None
    if mode != "off":
        pre_meta = take_snapshot(label="pre", run_id=run_id, mode=mode)

    # Start logs (dual)
    log_memory_event(
        event_text="snapshot_wrapper start",
        source=tool,
        tags=["tool", "snapshot", "start"],
        content={"run_id": run_id, "mode": mode, "db": Path(DB_PATH).as_posix(), "module": args.module},
        phase=REQUIRED_PHASE,
    )
    log_trace_event(
        description="snapshot_wrapper start",
        source=tool,
        tags=["tool", "snapshot", "start"],
        content={"run_id": run_id, "mode": mode},
        phase=REQUIRED_PHASE,
    )

    status = "ok"
    error: Optional[BaseException] = None
    result: Optional[Any] = None

    try:
        target = _resolve_callable(args.module)
        if target is not None:
            result = target(**target_args) if target_args else target()
    except BaseException as e:
        status = "error"
        error = e

    # Post snapshot + diff
    post_meta = None
    diff_summary = None
    if mode != "off":
        post_meta = take_snapshot(label="post", run_id=run_id, mode=mode)
        diff_summary = compare_snapshots(pre_meta, post_meta) if pre_meta else None

    # Audit line + index
    run_dir = Path(pre_meta["run_dir"] if pre_meta else Path(".").as_posix())
    write_audit_line(run_dir, {
        "ts": __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ", __import__("time").gmtime()),
        "tool": tool,
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "diff": diff_summary or {},
    })
    pre_cs = (pre_meta or {}).get("db_checksum")
    post_cs = (post_meta or {}).get("db_checksum")
    index_snapshot(run_id=run_id, run_dir=run_dir, pre_checksum=pre_cs, post_checksum=post_cs, status=status)

    # End logs (dual)
    log_memory_event(
        event_text="snapshot_wrapper done",
        source=tool,
        tags=["tool", "snapshot", "done"],
        content={"run_id": run_id, "status": status, "diff": diff_summary},
        phase=REQUIRED_PHASE,
    )
    log_trace_event(
        description="snapshot_wrapper done",
        source=tool,
        tags=["tool", "snapshot", "done"],
        content={"run_id": run_id, "status": status},
        phase=REQUIRED_PHASE,
    )

    # Console
    print(f"[snapshot] run_id={run_id} mode={mode}")
    if diff_summary:
        print(f"[snapshot] tables_changed={len(diff_summary.get('tables_changed', []))}")
    print(f"[snapshot] status={status}")

    if error:
        raise error

if __name__ == "__main__":
    run_cli()

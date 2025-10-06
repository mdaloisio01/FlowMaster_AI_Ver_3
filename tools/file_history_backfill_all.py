# tools/file_history_backfill_all.py
# Backfill ALL repo python files into configs/ironroot_file_history_with_dependencies.json
# - Path injection
# - Phase lock via ensure_phase()
# - Dual logging (start/report/done) with shared run_id
# - UTF-8 JSON writes, forward slashes
# - PRINT-ONLY by default (use --apply to write)

from boot.boot_path_initializer import inject_paths
inject_paths()

import argparse
import json
import os
import sys
import uuid
from pathlib import Path
from typing import Dict, List

from core.phase_control import ensure_phase, REQUIRED_PHASE
from core.sqlite_bootstrap import DB_PATH
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event

HISTORY_PATH = Path("configs/ironroot_file_history_with_dependencies.json")

def _rel(p: Path) -> str:
    return p.as_posix()

def _discover_files(roots: List[str]) -> List[str]:
    out: List[str] = []
    for r in roots:
        base = Path(r)
        if not base.exists():
            continue
        for p in base.rglob("*.py"):
            if "__pycache__" in p.parts:
                continue
            out.append(_rel(p))
    return sorted(set(out))

def _load_history() -> Dict:
    if HISTORY_PATH.exists():
        try:
            return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"history": {}}

def run_cli():
    ensure_phase()  # lock to REQUIRED_PHASE

    ap = argparse.ArgumentParser(description="Backfill ALL repo .py files into file-history", allow_abbrev=False)
    ap.add_argument("--roots", nargs="+", default=["core", "reflexes", "tools", "tests"],
                    help="Top-level directories to scan")
    ap.add_argument("--apply", action="store_true", help="Write changes")
    ap.add_argument("--print-report", action="store_true", help="Print JSON report")
    args = ap.parse_args()

    run_id = os.environ.get("RUN_ID") or f"file_history_backfill_all:{uuid.uuid4()}"
    tool = _rel(Path(__file__))

    # start
    log_memory_event(
        event_text="file_history_backfill_all start",
        source=tool,
        tags=["tool","history","start"],
        content={"run_id": run_id, "db": _rel(Path(DB_PATH)), "roots": args.roots, "target": _rel(HISTORY_PATH)},
        phase=REQUIRED_PHASE,
    )
    log_trace_event(
        description="file_history_backfill_all start",
        source=tool,
        tags=["tool","history","start"],
        content={"run_id": run_id},
        phase=REQUIRED_PHASE,
    )

    hist = _load_history()
    if "history" not in hist or not isinstance(hist["history"], dict):
        hist["history"] = {}

    discovered = _discover_files(args.roots)
    existing_keys = set(hist["history"].keys())
    to_add = [p for p in discovered if p not in existing_keys]

    report = {
        "target_file": _rel(HISTORY_PATH),
        "roots": args.roots,
        "discovered_count": len(discovered),
        "existing_count": len(existing_keys),
        "to_add_count": len(to_add),
        "to_add_sample": to_add[:25],  # preview only
        "apply": bool(args.apply),
    }

    if args.apply:
        HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
        for p in to_add:
            hist["history"][p] = {}  # minimal entry; no phase assumptions
        HISTORY_PATH.write_text(json.dumps(hist, ensure_ascii=False, indent=2), encoding="utf-8")

    # report + done
    log_memory_event(
        event_text="file_history_backfill_all report",
        source=tool,
        tags=["tool","history","report"],
        content={"run_id": run_id, "to_add_count": len(to_add)},
        phase=REQUIRED_PHASE,
    )
    log_trace_event(
        description="file_history_backfill_all done",
        source=tool,
        tags=["tool","history","done"],
        content={"run_id": run_id, "applied": bool(args.apply)},
        phase=REQUIRED_PHASE,
    )

    if args.print_report:
        print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    run_cli()

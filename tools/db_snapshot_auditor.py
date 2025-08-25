# tools/db_snapshot_auditor.py
# Phase-agnostic DB snapshot auditor.
# - Path injection required
# - Phase lock respected
# - Uses DB_PATH from core.sqlite_bootstrap (no hardcoded paths)
# - Dual logging: log_memory_event + log_trace_event
# - Tolerates legacy schemas (e.g., snapshot_index without run_dir)

from __future__ import annotations

from boot.boot_path_initializer import inject_paths
inject_paths()

import sys
import json
import argparse
import sqlite3
from pathlib import PurePosixPath
from typing import Any, Dict, List, Optional, Tuple

# Phase lock & DB path
try:
    from core.phase_control import REQUIRED_PHASE, ensure_phase, get_current_phase  # type: ignore
except Exception:  # pragma: no cover
    REQUIRED_PHASE = None
    def ensure_phase(_: Any) -> None:  # fallback no-op if missing
        return
    def get_current_phase() -> Optional[float]:  # fallback
        return None

from core.sqlite_bootstrap import DB_PATH  # single source of truth

# Dual logging
try:
    from core.memory_interface import log_memory_event  # positional-friendly
except Exception as e:  # pragma: no cover
    def log_memory_event(*args, **kwargs):
        # Last-resort fallback to keep the tool from crashing
        print(f"[memory-fallback] {args[0] if args else kwargs.get('event_text','')}", file=sys.stderr)

try:
    from core.trace_interface import log_trace_event  # expected in repo
except Exception:  # pragma: no cover
    def log_trace_event(*args, **kwargs):
        # Fallback: mirror into memory log so dual-logging is still observed
        msg = args[0] if args else kwargs.get("message", "")
        log_memory_event(msg, event_type="trace_fallback", tags=["trace", "fallback"], content=kwargs.get("content"))

# ---- helpers ----

def _open() -> sqlite3.Connection:
    # DB_PATH is a PurePosixPath (or str); sqlite3 accepts str-like path
    return sqlite3.connect(str(DB_PATH))

def _has_table(cur: sqlite3.Cursor, name: str) -> bool:
    cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,))
    return bool(cur.fetchone())

def _cols(cur: sqlite3.Cursor, table: str) -> List[str]:
    cur.execute("PRAGMA table_info(" + table + ")")
    return [r[1] for r in cur.fetchall()]

def _select_recent_snapshots(cur: sqlite3.Cursor, *, limit: int, run_id: Optional[str]) -> Tuple[List[Dict[str, Any]], bool]:
    """
    Returns (rows, has_run_dir_column)
    Rows contain keys: id, ts, run_id, mode, tables_changed, (run_dir if present)
    """
    has_run_dir = False
    columns = _cols(cur, "snapshot_index")
    has_run_dir = "run_dir" in columns  # legacy builds
    base_cols = ["id", "ts", "run_id", "mode", "tables_changed"]
    select_cols = ", ".join([c for c in base_cols if c in columns])
    if has_run_dir:
        select_cols += ", run_dir"

    where = ""
    params: Tuple[Any, ...] = ()
    if run_id:
        where = "WHERE run_id = ?"
        params = (run_id,)

    cur.execute(f"SELECT {select_cols} FROM snapshot_index {where} ORDER BY id DESC LIMIT {int(limit)}", params)
    rows = cur.fetchall()
    # Map rows to dict with only the fields we actually selected
    selected = select_cols.replace(" ", "").split(",")
    out: List[Dict[str, Any]] = []
    for r in rows:
        d = dict(zip(selected, r))
        # normalize any path-like strings to posix
        if "run_dir" in d and isinstance(d["run_dir"], str):
            d["run_dir"] = PurePosixPath(d["run_dir"]).as_posix()
        out.append(d)
    return out, has_run_dir

# ---- CLI ----

def run_cli() -> None:
    ensure_phase(REQUIRED_PHASE)  # phase lock (no-op fallback if function is stubbed)

    ap = argparse.ArgumentParser(description="DB snapshot auditor (phase-agnostic).")
    ap.add_argument("--run-id", dest="run_id", default=None)
    ap.add_argument("--limit", dest="limit", type=int, default=20)
    args = ap.parse_args()

    # start logs (dual)
    log_memory_event(f"db_snapshot_auditor start (run_id={args.run_id}, limit={args.limit})",
                     event_type="tool_log", tags=["tool","snapshot","audit"], phase=get_current_phase())
    log_trace_event("db_snapshot_auditor start",
                    tags=["tool","snapshot","audit"],
                    content={"run_id": args.run_id, "limit": args.limit, "phase": get_current_phase()})

    with _open() as con:
        cur = con.cursor()
        if not _has_table(cur, "snapshot_index"):
            # hard fail: required by phases >= 0.3
            reason = "snapshot_index table missing"
            log_memory_event(f"db_snapshot_auditor error — {reason}",
                             event_type="error", tags=["tool","snapshot","audit"], phase=get_current_phase(),
                             content={"reason": reason})
            log_trace_event("db_snapshot_auditor error", tags=["tool","snapshot","audit"], content={"reason": reason})
            print(json.dumps({"ok": False, "reason": reason}, indent=2))
            sys.exit(2)

        rows, has_run_dir = _select_recent_snapshots(cur, limit=args.limit, run_id=args.run_id)

    report = {
        "ok": True,
        "db": str(DB_PATH),
        "phase": get_current_phase(),
        "has_run_dir_column": has_run_dir,
        "count": len(rows),
        "rows": rows,
    }

    # report logs (dual)
    log_memory_event("db_snapshot_auditor report",
                     event_type="tool_log", tags=["tool","snapshot","audit"], phase=get_current_phase(),
                     content=report)
    log_trace_event("db_snapshot_auditor report",
                    tags=["tool","snapshot","audit"], content=report)

    print(json.dumps(report, indent=2))
    # done logs (dual)
    log_memory_event("db_snapshot_auditor done",
                     event_type="tool_log", tags=["tool","snapshot","done"], phase=get_current_phase())
    log_trace_event("db_snapshot_auditor done", tags=["tool","snapshot","done"])


if __name__ == "__main__":
    run_cli()

# tools/tools_check_db_counts.py
from __future__ import annotations

from boot.boot_path_initializer import inject_paths
inject_paths()

import sqlite3
from pathlib import Path

from core.phase_control import REQUIRED_PHASE, ensure_phase
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event


DB_PATH = Path("root/will_data.db")  # unified path per Phase 0.4 guidance


def run_cli() -> None:
    ensure_phase()
    tool_name = Path(__file__).as_posix()

    log_memory_event(
        "tools_check_db_counts start",
        source=tool_name,
        tags=["tool", "start", "tools_check_db_counts"],
        content="starting",
        phase=REQUIRED_PHASE,
    )

    if not DB_PATH.exists():
        print(f"DB not found: {DB_PATH.as_posix()}")
        raise SystemExit(7)

    with sqlite3.connect(DB_PATH.as_posix()) as conn:
        cur = conn.cursor()
        counts = {}
        for table in ("memory_events", "trace_events", "boot_events"):
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                counts[table] = cur.fetchone()[0]
            except Exception:
                counts[table] = None

    print("DB counts:", counts)

    log_trace_event(
        "tools_check_db_counts done",
        source=tool_name,
        tags=["tool", "done", "tools_check_db_counts"],
        phase=REQUIRED_PHASE,
    )


if __name__ == "__main__":
    run_cli()

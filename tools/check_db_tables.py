from __future__ import annotations
from boot.boot_path_initializer import inject_paths
inject_paths()

import argparse
import sqlite3
from pathlib import Path
from typing import Iterable, List

from core.phase_control import ensure_phase, REQUIRED_PHASE
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event
from core.sqlite_bootstrap import DB_PATH, create_tables

REQUIRED_TABLES = (
    "memory_events",
    "trace_events",
    "boot_events",
    "manifest",
    "reflex_registry",
)


def _list_tables(conn: sqlite3.Connection) -> List[str]:
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    return sorted([r[0] for r in cur.fetchall()])


def run_cli() -> None:
    ensure_phase()
    src = Path(__file__).as_posix()

    parser = argparse.ArgumentParser(description="Check presence of required DB tables.")
    _ = parser.parse_args()

    log_memory_event(
        event_text="check_db_tables start",
        source=src,
        tags=["tool", "start", "db_check"],
        content={"db_path": DB_PATH.as_posix()},
        phase=REQUIRED_PHASE,
    )

    create_tables()
    missing = []
    with sqlite3.connect(DB_PATH.as_posix()) as conn:
        names = set(_list_tables(conn))
        for table in REQUIRED_TABLES:
            if table not in names:
                missing.append(table)

    if missing:
        print(f"❌ Missing tables: {', '.join(missing)}")
    else:
        # Include sqlite_sequence if autoincrement used (may exist)
        names_display = ", ".join(sorted(names))
        print(f"✅ DB tables OK: {names_display}")

    log_trace_event(
        description="check_db_tables done",
        source=src,
        tags=["tool", "done", "db_check"],
        content={"missing": missing},
        phase=REQUIRED_PHASE,
    )


if __name__ == "__main__":
    run_cli()

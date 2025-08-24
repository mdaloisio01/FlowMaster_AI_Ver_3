# reflexes/reflex_core/reflex_table_tick.py
# Canonical Reflex Template — creates/updates a small test table to force a DB diff.

from boot.boot_path_initializer import inject_paths
inject_paths()

import sqlite3
from pathlib import Path

from core.phase_control import ensure_phase, REQUIRED_PHASE
from core.sqlite_bootstrap import DB_PATH
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event


def run_cli():
    ensure_phase()  # fail-closed if not REQUIRED_PHASE

    # Force a deterministic DB change
    with sqlite3.connect(Path(DB_PATH).as_posix()) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS test_ticks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            """
        )
        conn.execute("INSERT INTO test_ticks DEFAULT VALUES;")
        conn.commit()

    # Dual logging
    src = __file__.replace("\\", "/")
    log_memory_event(
        event_text="reflex_table_tick inserted row",
        source=src,
        tags=["reflex", "test", "snapshot"],
        content={"table": "test_ticks"},
        phase=REQUIRED_PHASE,
    )
    log_trace_event(
        description="reflex_table_tick executed",
        source=src,
        tags=["reflex", "test", "snapshot"],
        content={"table": "test_ticks", "result": "ok"},
        phase=REQUIRED_PHASE,
    )

    print("✅ table_tick ok")


if __name__ == "__main__":
    run_cli()

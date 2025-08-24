# core/sqlite_bootstrap.py
# Creates/maintains the Phase 0.4 database schema in root/will_data.db
# Tables:
#   - memory_events(id, ts, event_json)
#   - trace_events(id, ts, event_json)
#   - boot_events(id, ts, event_json)
#   - manifest(file_path PK, phase, dependencies_json, created_at)
#   - reflex_registry(name PK, module_path, phase, active, metadata_json, created_at)

from __future__ import annotations

from boot.boot_path_initializer import inject_paths
inject_paths()

import sqlite3
from pathlib import Path
from typing import Iterable

from core.phase_control import REQUIRED_PHASE, ensure_phase, get_current_phase
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event

DB_PATH = Path("root/will_data.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def _exec_many(conn: sqlite3.Connection, stmts: Iterable[str]) -> None:
    cur = conn.cursor()
    for s in stmts:
        cur.execute(s)
    conn.commit()


def create_tables() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH.as_posix()) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")

        stmts = [
            # Core event chains (Phase 0.x)
            """
            CREATE TABLE IF NOT EXISTS memory_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                event_json TEXT NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS trace_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                event_json TEXT NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS boot_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                event_json TEXT NOT NULL
            );
            """,
            # Phase 0.4-compatible tables used by tests/tools
            """
            CREATE TABLE IF NOT EXISTS manifest (
                file_path TEXT PRIMARY KEY,
                phase REAL NOT NULL,
                dependencies_json TEXT NOT NULL DEFAULT '[]',
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS reflex_registry (
                name TEXT PRIMARY KEY,
                module_path TEXT NOT NULL,
                phase REAL NOT NULL,
                active INTEGER NOT NULL DEFAULT 1,
                metadata_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            """,
        ]
        _exec_many(conn, stmts)


def run_cli() -> None:
    # Enforce phase for CLI operation
    ensure_phase()
    cur_phase = get_current_phase()

    log_memory_event(
        event_text="sqlite_bootstrap start",
        source=Path(__file__).as_posix(),
        tags=["db", "start", "bootstrap"],
        content={"db_path": DB_PATH.as_posix(), "phase_required": REQUIRED_PHASE, "phase_current": cur_phase},
        phase=REQUIRED_PHASE,
    )

    create_tables()

    log_trace_event(
        description="sqlite_bootstrap done",
        source=Path(__file__).as_posix(),
        tags=["db", "done", "bootstrap"],
        content={"db_path": DB_PATH.as_posix()},
        phase=REQUIRED_PHASE,
    )

    print(f"SQLite bootstrap OK @ {DB_PATH.as_posix()}")


if __name__ == "__main__":
    run_cli()

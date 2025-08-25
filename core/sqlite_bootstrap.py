# core/sqlite_bootstrap.py

from boot.boot_path_initializer import inject_paths  # required path injection
inject_paths()

import os
import sqlite3
import json
import datetime
import contextlib
from pathlib import Path, PurePosixPath
from typing import Optional, Dict, Any, Iterable, List

# Single source of truth for DB path (must expose .as_posix() for early tests)
DB_PATH: PurePosixPath = PurePosixPath("root/will_data.db")


def _connect() -> sqlite3.Connection:
    """
    Returns a sqlite3 connection to the IronRoot database.
    Callers must not hardcode paths; always use DB_PATH.
    """
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(os.fspath(DB_PATH))
    con.execute("PRAGMA foreign_keys = ON;")
    return con


def _rows_to_dicts(cursor: sqlite3.Cursor, rows: Iterable[Iterable[Any]]) -> List[Dict[str, Any]]:
    cols = [d[0] for d in cursor.description]
    return [dict(zip(cols, r)) for r in rows]


def ensure_tables() -> None:
    """
    Create required tables if they do not already exist.
    This is phase-agnostic and safe to run multiple times.
    """
    with contextlib.closing(_connect()) as con, contextlib.closing(con.cursor()) as cur:
        # boot_events — general boot/report log table used by early-phase tests
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS boot_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                event TEXT,
                details TEXT
            )
            """
        )

        # manifest — file registry
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS manifest (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                added_ts TEXT,
                phase TEXT
            )
            """
        )

        # memory_events — for dual-logging memory track
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS memory_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                tag TEXT NOT NULL,
                payload TEXT
            )
            """
        )

        # reflex_registry — registry of reflex/tool handlers
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS reflex_registry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                reflex_name TEXT NOT NULL,
                module TEXT,
                path TEXT,
                enabled INTEGER DEFAULT 1
            )
            """
        )

        # trace_events — for dual-logging trace track
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS trace_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                level TEXT NOT NULL,
                tag TEXT NOT NULL,
                message TEXT,
                context TEXT
            )
            """
        )

        # snapshot_index — used by snapshot tools
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS snapshot_index (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                run_id TEXT NOT NULL,
                mode TEXT NOT NULL,
                tables_changed INTEGER DEFAULT 0
            )
            """
        )

        # test_ticks — helper table used by tests
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS test_ticks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                tick TEXT NOT NULL
            )
            """
        )

        con.commit()


# Back-compat alias expected by some tools (e.g., tools.check_db_tables)
def create_tables() -> None:
    """Alias to ensure_tables(), provided for backward compatibility."""
    ensure_tables()


def list_tables() -> List[str]:
    """Return a sorted list of tables in the database."""
    with contextlib.closing(_connect()) as con, contextlib.closing(con.cursor()) as cur:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return sorted([r[0] for r in cur.fetchall()])


def insert_boot_report_entry(event: str, *, ts: Optional[str] = None, details: Optional[Dict[str, Any]] = None) -> int:
    """
    Public API expected by early-phase tests.
    Inserts a row into boot_events and returns the row id.
    """
    ensure_tables()
    if ts is None:
        ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    payload = json.dumps(details, ensure_ascii=False) if isinstance(details, dict) else None

    with contextlib.closing(_connect()) as con, contextlib.closing(con.cursor()) as cur:
        cur.execute(
            "INSERT INTO boot_events (ts, event, details) VALUES (?, ?, ?)",
            (ts, event, payload),
        )
        con.commit()
        return int(cur.lastrowid)


def bootstrap() -> None:
    """Idempotent bootstrap entrypoint used by `py -m core.sqlite_bootstrap`."""
    ensure_tables()


if __name__ == "__main__":
    bootstrap()
    print(f"SQLite bootstrap OK @ {DB_PATH.as_posix()}")


__all__ = [
    "DB_PATH",
    "ensure_tables",
    "create_tables",  # back-compat
    "list_tables",
    "insert_boot_report_entry",
    "bootstrap",
]

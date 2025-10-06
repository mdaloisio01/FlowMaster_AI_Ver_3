# core/manifest_db.py
from boot.boot_path_initializer import inject_paths
inject_paths()

import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from core.phase_control import REQUIRED_PHASE, ensure_phase
from core.sqlite_bootstrap import DB_PATH, ensure_tables
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event

def _connect() -> sqlite3.Connection:
    ensure_tables()
    return sqlite3.connect(Path(DB_PATH).as_posix())

def fetch_all_manifest() -> List[Dict[str, Any]]:
    ensure_phase(REQUIRED_PHASE)
    run_id = f"manifest_db_fetch"
    log_memory_event("manifest_db.fetch_all_manifest:start", source=__file__, tags=["tool","start"], phase=REQUIRED_PHASE, content={"run_id":run_id})
    log_trace_event("manifest_db.fetch_all_manifest:start", source=__file__, tags=["tool","start"], phase=REQUIRED_PHASE, content={"run_id":run_id})

    with _connect() as con:
        cur = con.execute("PRAGMA table_info(manifest);")
        if not cur.fetchall():
            # ensure table exists
            con.execute("""
                CREATE TABLE IF NOT EXISTS manifest (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT UNIQUE NOT NULL,
                    added_ts TEXT,
                    phase TEXT
                )
            """)
        rows = con.execute("SELECT id, path, added_ts, phase FROM manifest ORDER BY id ASC;").fetchall()
        out = [{"id":r[0], "path":r[1], "added_ts":r[2], "phase":r[3]} for r in rows]

    log_memory_event("manifest_db.fetch_all_manifest:report", source=__file__, tags=["tool","report"], phase=REQUIRED_PHASE, content={"run_id":run_id,"count":len(out)})
    log_trace_event("manifest_db.fetch_all_manifest:done", source=__file__, tags=["tool","done"], phase=REQUIRED_PHASE, content={"run_id":run_id})
    return out

def upsert_manifest_path(path: str, phase: float, added_ts: Optional[str] = None) -> None:
    ensure_phase(REQUIRED_PHASE)
    run_id = f"manifest_db_upsert:{path}"
    log_memory_event("manifest_db.upsert:start", source=__file__, tags=["tool","start"], phase=REQUIRED_PHASE, content={"run_id":run_id,"path":path})
    log_trace_event("manifest_db.upsert:start", source=__file__, tags=["tool","start"], phase=REQUIRED_PHASE, content={"run_id":run_id,"path":path})

    with _connect() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS manifest (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                added_ts TEXT,
                phase TEXT
            )
        """)
        con.execute("""
            INSERT INTO manifest (path, added_ts, phase)
            VALUES (?, ?, ?)
            ON CONFLICT(path) DO UPDATE SET
                added_ts=COALESCE(excluded.added_ts, manifest.added_ts),
                phase=excluded.phase
        """, (path.replace("\\","/"), added_ts, str(phase)))
        con.commit()

    log_memory_event("manifest_db.upsert:done", source=__file__, tags=["tool","done"], phase=REQUIRED_PHASE, content={"run_id":run_id,"path":path})
    log_trace_event("manifest_db.upsert:done", source=__file__, tags=["tool","done"], phase=REQUIRED_PHASE, content={"run_id":run_id})

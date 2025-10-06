# core/reflex_registry_db.py
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

def fetch_all_reflexes() -> List[Dict[str, Any]]:
    ensure_phase(REQUIRED_PHASE)
    run_id = "reflex_registry_fetch"
    log_memory_event("reflex_registry.fetch:start", source=__file__, tags=["tool","start"], phase=REQUIRED_PHASE, content={"run_id":run_id})
    log_trace_event("reflex_registry.fetch:start", source=__file__, tags=["tool","start"], phase=REQUIRED_PHASE, content={"run_id":run_id})

    with _connect() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS reflex_registry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                reflex_name TEXT NOT NULL,
                module TEXT NOT NULL,
                path TEXT NOT NULL,
                enabled INTEGER DEFAULT 1
            )
        """)
        rows = con.execute("SELECT id, ts, reflex_name, module, path, enabled FROM reflex_registry ORDER BY id ASC;").fetchall()
        out = [{"id":r[0],"ts":r[1],"reflex_name":r[2],"module":r[3],"path":r[4],"enabled":int(r[5])} for r in rows]

    log_memory_event("reflex_registry.fetch:report", source=__file__, tags=["tool","report"], phase=REQUIRED_PHASE, content={"run_id":run_id,"count":len(out)})
    log_trace_event("reflex_registry.fetch:done", source=__file__, tags=["tool","done"], phase=REQUIRED_PHASE, content={"run_id":run_id})
    return out

def register_reflex(*, ts: str, reflex_name: str, module: str, path: str, enabled: bool = True) -> int:
    ensure_phase(REQUIRED_PHASE)
    run_id = f"reflex_registry_register:{reflex_name}"
    log_memory_event("reflex_registry.register:start", source=__file__, tags=["tool","start"], phase=REQUIRED_PHASE, content={"run_id":run_id,"reflex_name":reflex_name})
    log_trace_event("reflex_registry.register:start", source=__file__, tags=["tool","start"], phase=REQUIRED_PHASE, content={"run_id":run_id,"reflex_name":reflex_name})

    with _connect() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS reflex_registry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                reflex_name TEXT NOT NULL,
                module TEXT NOT NULL,
                path TEXT NOT NULL,
                enabled INTEGER DEFAULT 1
            )
        """)
        cur = con.execute("""
            INSERT INTO reflex_registry (ts, reflex_name, module, path, enabled)
            VALUES (?, ?, ?, ?, ?)
        """, (ts, reflex_name, module, path.replace("\\","/"), 1 if enabled else 0))
        con.commit()
        new_id = int(cur.lastrowid)

    log_memory_event("reflex_registry.register:done", source=__file__, tags=["tool","done"], phase=REQUIRED_PHASE, content={"run_id":run_id,"id":new_id})
    log_trace_event("reflex_registry.register:done", source=__file__, tags=["tool","done"], phase=REQUIRED_PHASE, content={"run_id":run_id,"id":new_id})
    return new_id

# core/reflex_registry_db.py
# Helper APIs for the reflex_registry table in root/will_data.db

from __future__ import annotations

from boot.boot_path_initializer import inject_paths
inject_paths()

import json
import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any, List

from core.sqlite_bootstrap import DB_PATH, create_tables  # ensures path consistency


def _conn() -> sqlite3.Connection:
    create_tables()  # idempotent safety
    return sqlite3.connect(DB_PATH.as_posix())


def register_reflex(
    name: str,
    *,
    module_path: str,
    phase: float,
    active: bool = True,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    meta_json = json.dumps(metadata or {}, ensure_ascii=False)
    with _conn() as conn:
        conn.execute(
            """
            INSERT INTO reflex_registry(name, module_path, phase, active, metadata_json)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
              module_path=excluded.module_path,
              phase=excluded.phase,
              active=excluded.active,
              metadata_json=excluded.metadata_json
            """,
            (name, module_path.replace("\\", "/"), float(phase), 1 if active else 0, meta_json),
        )
        conn.commit()


def get_reflex(name: str) -> Optional[Dict[str, Any]]:
    with _conn() as conn:
        cur = conn.execute(
            "SELECT name, module_path, phase, active, metadata_json, created_at FROM reflex_registry WHERE name=?",
            (name,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return {
            "name": row[0],
            "module_path": row[1],
            "phase": float(row[2]),
            "active": bool(row[3]),
            "metadata": json.loads(row[4] or "{}"),
            "created_at": row[5],
        }


def list_reflexes(limit: int = 1000) -> List[Dict[str, Any]]:
    with _conn() as conn:
        cur = conn.execute(
            "SELECT name, module_path, phase, active, metadata_json, created_at FROM reflex_registry ORDER BY name LIMIT ?",
            (int(limit),),
        )
        out: List[Dict[str, Any]] = []
        for row in cur.fetchall():
            out.append(
                {
                    "name": row[0],
                    "module_path": row[1],
                    "phase": float(row[2]),
                    "active": bool(row[3]),
                    "metadata": json.loads(row[4] or "{}"),
                    "created_at": row[5],
                }
            )
        return out

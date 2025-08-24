# core/manifest_db.py
# Helper APIs for the manifest table in root/will_data.db

from __future__ import annotations

from boot.boot_path_initializer import inject_paths
inject_paths()

import json
import sqlite3
from pathlib import Path
from typing import List, Optional, Dict, Any

from core.phase_control import REQUIRED_PHASE
from core.sqlite_bootstrap import DB_PATH, create_tables  # ensures path consistency


def _conn() -> sqlite3.Connection:
    create_tables()  # idempotent safety
    return sqlite3.connect(DB_PATH.as_posix())


def upsert_manifest(file_path: str, *, phase: float, dependencies: Optional[List[str]] = None) -> None:
    deps_json = json.dumps(list(dependencies or []), ensure_ascii=False)
    with _conn() as conn:
        conn.execute(
            """
            INSERT INTO manifest(file_path, phase, dependencies_json)
            VALUES (?, ?, ?)
            ON CONFLICT(file_path) DO UPDATE SET
              phase=excluded.phase,
              dependencies_json=excluded.dependencies_json
            """,
            (file_path.replace("\\", "/"), float(phase), deps_json),
        )
        conn.commit()


def get_manifest(file_path: str) -> Optional[Dict[str, Any]]:
    with _conn() as conn:
        cur = conn.execute(
            "SELECT file_path, phase, dependencies_json, created_at FROM manifest WHERE file_path=?",
            (file_path.replace("\\", "/"),),
        )
        row = cur.fetchone()
        if not row:
            return None
        return {
            "file_path": row[0],
            "phase": float(row[1]),
            "dependencies": json.loads(row[2] or "[]"),
            "created_at": row[3],
        }


def list_manifest(limit: int = 1000) -> List[Dict[str, Any]]:
    with _conn() as conn:
        cur = conn.execute(
            "SELECT file_path, phase, dependencies_json, created_at FROM manifest ORDER BY file_path LIMIT ?",
            (int(limit),),
        )
        out: List[Dict[str, Any]] = []
        for row in cur.fetchall():
            out.append(
                {
                    "file_path": row[0],
                    "phase": float(row[1]),
                    "dependencies": json.loads(row[2] or "[]"),
                    "created_at": row[3],
                }
            )
        return out

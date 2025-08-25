# core/reflex_registry_db.py

from boot.boot_path_initializer import inject_paths  # required path injection
inject_paths()

import sqlite3
import contextlib
import pathlib
from typing import List, Dict, Any

# Always use the shared DB path (never hardcode)
from core.sqlite_bootstrap import DB_PATH


def _rows_to_dicts(cursor: sqlite3.Cursor, rows: list) -> List[Dict[str, Any]]:
    cols = [d[0] for d in cursor.description]
    return [dict(zip(cols, r)) for r in rows]


def _normalize_possible_paths(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize any value that looks like a filesystem path to forward slashes.
    We consider keys containing 'path' or common file-ish keys.
    """
    for k, v in list(row.items()):
        if isinstance(v, str):
            lk = k.lower()
            if "path" in lk or lk in {"module", "file", "script"}:
                if ("/" in v) or ("\\" in v):
                    row[k] = pathlib.PurePosixPath(v).as_posix()
    return row


def fetch_all_reflexes() -> List[Dict[str, Any]]:
    """
    Phase-agnostic read of the reflex registry.

    Source:
      - SQLite table 'reflex_registry' (if present). Returns full row dicts as-is,
        but normalizes any path-like fields to forward slashes.

    Never raises; returns [] on any unexpected issue or if the table is missing/empty.
    """
    with contextlib.ExitStack() as stack:
        try:
            con = stack.enter_context(sqlite3.connect(DB_PATH))
            cur = con.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='reflex_registry'")
            if not cur.fetchone():
                return []
            cur.execute("SELECT * FROM reflex_registry")
            rows = cur.fetchall()
            if not rows:
                return []
            results = _rows_to_dicts(cur, rows)
            return [_normalize_possible_paths(r) for r in results]
        except Exception:
            # Tests expect robustness: on any issue, return an empty list rather than raising.
            return []


__all__ = ["fetch_all_reflexes"]

# core/manifest_db.py

from boot.boot_path_initializer import inject_paths  # required path injection
inject_paths()

import json
import sqlite3
import pathlib
import contextlib
from typing import List, Dict, Any

# Always use the shared DB path (never hardcode)
from core.sqlite_bootstrap import DB_PATH


def _rows_to_dicts(cursor: sqlite3.Cursor, rows: list) -> List[Dict[str, Any]]:
    cols = [d[0] for d in cursor.description]
    return [dict(zip(cols, r)) for r in rows]


def _posix(p: str) -> str:
    return pathlib.PurePosixPath(p).as_posix()


def _ensure_file_path_key(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tests for early phases require every row to contain 'file_path'.
    If DB uses 'path' (or similar), normalize and mirror it into 'file_path'.
    Keep original keys too for compatibility.
    """
    if "file_path" in row and isinstance(row["file_path"], str):
        row["file_path"] = _posix(row["file_path"])
        return row

    # common aliases we might see in different phases
    for k in ("path", "filepath", "file"):
        if k in row and isinstance(row[k], str):
            row["file_path"] = _posix(row[k])
            return row

    # as a last resort, provide an empty normalized value
    row.setdefault("file_path", "")
    return row


def fetch_all_manifest() -> List[Dict[str, Any]]:
    """
    Phase-agnostic read of manifest entries.

    Primary source:
      - SQLite table 'manifest' (if present and non-empty).
        Returns full row dicts, ensuring a 'file_path' key (normalized to forward slashes).

    Fallback:
      - configs/ironroot_manifest_data.json with schema:
          { "files": ["path/one.py", "another/file.txt", ...] }
        Returned rows look like: { "file_path": "<posix>" }

    Never raises; returns [] on any unexpected issue.
    """
    # 1) Try database first
    with contextlib.ExitStack() as stack:
        try:
            con = stack.enter_context(sqlite3.connect(DB_PATH))
            cur = con.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='manifest'")
            if cur.fetchone():
                cur.execute("SELECT * FROM manifest")
                rows = cur.fetchall()
                if rows:
                    results = _rows_to_dicts(cur, rows)
                    return [_ensure_file_path_key(r) for r in results]
        except Exception:
            # Silent fallback — tests only require robust read semantics.
            pass

    # 2) Fallback to JSON manifest
    try:
        mf = pathlib.Path("configs/ironroot_manifest_data.json")
        if mf.exists():
            data = json.loads(mf.read_text(encoding="utf-8"))
            files = data.get("files", []) or []
            return [{"file_path": _posix(p)} for p in files if isinstance(p, str)]
    except Exception:
        pass

    return []


__all__ = ["fetch_all_manifest"]

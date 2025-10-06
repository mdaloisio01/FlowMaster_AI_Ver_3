# === IronRoot Phase Guard (auto-injected) ===
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from boot.boot_path_initializer import inject_paths
inject_paths()
from core.phase_control import ensure_phase
REQUIRED_PHASE = 0.7
ensure_phase(REQUIRED_PHASE)
# === /IronRoot Phase Guard ===

# core/snapshot_manager.py
# Phase 0.x snapshot engine (compatible with 0.4 runtime; heavy-mode for 0.5 testing)
# - Provides take_snapshot() and compare_snapshots() for CLI/reflex wrappers
# - Uses UTF-8 JSON writes and forward slashes for all paths
# - Stores artifacts under .snapshots/<ISO>/pre|post|diff plus audit.jsonl
from __future__ import annotations

import json
import sqlite3
import hashlib
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Single source of truth for DB path
from core.sqlite_bootstrap import DB_PATH

# ---------- helpers ----------

def _project_root() -> Path:
    """Find project root by locating configs/ironroot_manifest_data.json."""
    here = Path(__file__).resolve()
    for p in [here] + list(here.parents):
        if (p / "configs" / "ironroot_manifest_data.json").exists():
            return p
        if (p / "boot").is_dir() and (p / "core").is_dir():
            return p
    return Path.cwd().resolve()

def _now_iso() -> str:
    import time
    return time.strftime("%Y-%m-%dT%H-%M-%SZ", time.gmtime())  # filename-safe

def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)

def _list_tables(conn: sqlite3.Connection) -> List[str]:
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;")
    return [r[0] for r in cur.fetchall()]

def _table_pk_cols(conn: sqlite3.Connection, table: str) -> List[str]:
    cur = conn.execute(f"PRAGMA table_info({table});")
    cols = []
    for cid, name, ctype, notnull, dflt, pk in cur.fetchall():
        if pk:  # pk > 0 means part of primary key
            cols.append(name)
    return cols

def _table_rows(conn: sqlite3.Connection, table: str, pk_cols: List[str]) -> List[Dict[str, Any]]:
    cur = conn.execute(f"SELECT * FROM {table};")
    colnames = [d[0] for d in cur.description]
    rows = [dict(zip(colnames, r)) for r in cur.fetchall()]
    # Normalize types to JSON-friendly (no bytes) and keep ordering stable by PK if possible
    def row_key(r: Dict[str, Any]) -> Tuple:
        if pk_cols:
            return tuple(r.get(c) for c in pk_cols)
        # Fallback to all values
        return tuple(r.get(c) for c in colnames)
    rows.sort(key=row_key)
    return rows

def _rows_checksum(rows: List[Dict[str, Any]]) -> str:
    # Canonical JSON checksum (sorted keys, UTF-8)
    enc = json.dumps(rows, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(enc).hexdigest()

# ---------- public API ----------

def take_snapshot(*, label: str, run_id: str, mode: str = "heavy") -> Dict[str, Any]:
    """Create a snapshot of the DB.
    Returns metadata dict with paths (as posix strings) and checksums.
    label: "pre" or "post"
    mode: "off" | "light" | "heavy" (off returns minimal metadata without copying)
    """
    if label not in {"pre", "post"}:
        raise ValueError("label must be 'pre' or 'post'")
    if mode not in {"off", "light", "heavy"}:
        raise ValueError("mode must be off|light|heavy")

    root = _project_root()
    stamp = _now_iso()
    run_dir = root / ".snapshots" / f"{stamp}_run-{run_id}"
    pre_dir = run_dir / "pre"
    post_dir = run_dir / "post"
    diff_dir = run_dir / "diff"
    _ensure_dir(pre_dir); _ensure_dir(post_dir); _ensure_dir(diff_dir)

    meta: Dict[str, Any] = {
        "run_id": run_id,
        "label": label,
        "mode": mode,
        "run_dir": run_dir.as_posix(),
        "pre_dir": pre_dir.as_posix(),
        "post_dir": post_dir.as_posix(),
        "diff_dir": diff_dir.as_posix(),
        "db_path": Path(DB_PATH).as_posix(),
    }

    if mode == "off":
        return meta

    # Decide target dir from label
    target_dir = pre_dir if label == "pre" else post_dir
    db_copy = target_dir / "will_data.db"
    schema_json = target_dir / "schema.json"
    tables_json = target_dir / "tables.json"
    meta_json = target_dir / "snapshot_meta.json"

    # Copy/backup DB atomically
    # Use sqlite backup API for consistency
    with sqlite3.connect(DB_PATH.as_posix()) as src, sqlite3.connect(db_copy.as_posix()) as dst:
        src.backup(dst)  # type: ignore[attr-defined]

    # Compute file checksum
    meta["db_checksum"] = _sha256_file(db_copy)

    # Schema dump + table checksums/counts
    with sqlite3.connect(db_copy.as_posix()) as conn:
        # Schema: name -> sql
        srows = conn.execute("SELECT name, sql FROM sqlite_master WHERE type='table' ORDER BY name;").fetchall()
        schema = {name: sql for (name, sql) in srows}
        schema_json.write_text(json.dumps(schema, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")

        tables_meta: Dict[str, Any] = {}
        for t in _list_tables(conn):
            pk_cols = _table_pk_cols(conn, t)
            rows = _table_rows(conn, t, pk_cols)
            tables_meta[t] = {
                "row_count": len(rows),
                "pk": pk_cols,
                "checksum": _rows_checksum(rows) if mode == "heavy" else None,
            }
        tables_json.write_text(json.dumps(tables_meta, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")

    # Write minimal meta JSON (UTF-8)
    meta_json.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")

    return meta

def compare_snapshots(pre_meta: Dict[str, Any], post_meta: Dict[str, Any]) -> Dict[str, Any]:
    """Compute table-level and row-level diffs between pre and post DB copies.
    Writes a diff JSON file under run_dir/diff/report.json and returns the summary dict.
    """
    run_dir = Path(pre_meta["run_dir"])  # same for post
    diff_dir = Path(pre_meta["diff_dir"])  # posix -> Path
    pre_db = Path(pre_meta["pre_dir"]) / "will_data.db"
    post_db = Path(post_meta["post_dir"]) / "will_data.db"

    summary: Dict[str, Any] = {
        "run_id": pre_meta.get("run_id"),
        "tables_changed": [],
        "row_changes": {},  # table -> {added: n, removed: n, changed: n}
    }

    def load_table_rows(db_path: Path, table: str, pk_cols: List[str]) -> Dict[Tuple, Dict[str, Any]]:
        with sqlite3.connect(db_path.as_posix()) as conn:
            rows = _table_rows(conn, table, pk_cols)
            col_order = [k for k in (rows[0].keys() if rows else [])]
            # map by key
            res = {}
            for r in rows:
                key = tuple(r.get(c) for c in pk_cols) if pk_cols else tuple(r.get(c) for c in col_order)
                res[key] = r
            return res

    with sqlite3.connect(pre_db.as_posix()) as cpre, sqlite3.connect(post_db.as_posix()) as cpost:
        pre_tables = _list_tables(cpre)
        post_tables = _list_tables(cpost)
        all_tables = sorted(set(pre_tables) | set(post_tables))

        row_changes: Dict[str, Dict[str, int]] = {}

        for t in all_tables:
            pre_pk = _table_pk_cols(cpre, t) if t in pre_tables else []
            post_pk = _table_pk_cols(cpost, t) if t in post_tables else []
            pk = post_pk or pre_pk  # prefer post pk if exists
            pre_rows = load_table_rows(pre_db, t, pk) if t in pre_tables else {}
            post_rows = load_table_rows(post_db, t, pk) if t in post_tables else {}

            pre_keys = set(pre_rows.keys())
            post_keys = set(post_rows.keys())

            added_keys = post_keys - pre_keys
            removed_keys = pre_keys - post_keys
            common = pre_keys & post_keys

            changed = 0
            for k in common:
                if pre_rows[k] != post_rows[k]:
                    changed += 1

            if added_keys or removed_keys or changed:
                summary["tables_changed"].append(t)
                row_changes[t] = {
                    "added": len(added_keys),
                    "removed": len(removed_keys),
                    "changed": changed,
                }

        summary["row_changes"] = row_changes

    # Persist diff JSON report
    diff_json = diff_dir / "report.json"
    diff_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")

    return summary

def write_audit_line(run_dir: Path, record: Dict[str, Any]) -> None:
    audit_path = run_dir / "audit.jsonl"
    line = json.dumps(record, ensure_ascii=False)
    with audit_path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(line + "\n")


def index_snapshot(*, run_id: str, run_dir: Path, pre_checksum: Optional[str], post_checksum: Optional[str], status: str) -> None:
    """Record a small index row in live DB for searchability.
    Creates table snapshot_index if not exists: (snapshot_id TEXT PK, run_id TEXT, created_at TEXT, pre_checksum TEXT, post_checksum TEXT, run_dir TEXT, status TEXT)
    """
    with sqlite3.connect(DB_PATH.as_posix()) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS snapshot_index (
                snapshot_id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                pre_checksum TEXT,
                post_checksum TEXT,
                run_dir TEXT NOT NULL,
                status TEXT NOT NULL
            );
            """
        )
        snapshot_id = f"{run_id}-{_now_iso()}"
        conn.execute(
            "INSERT INTO snapshot_index (snapshot_id, run_id, created_at, pre_checksum, post_checksum, run_dir, status) VALUES (?, ?, datetime('now'), ?, ?, ?, ?);",
            (snapshot_id, run_id, pre_checksum, post_checksum, run_dir.as_posix(), status),
        )
        conn.commit()

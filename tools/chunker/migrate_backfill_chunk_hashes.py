# /tools/chunker/migrate_backfill_chunk_hashes.py
"""
Backfill + Dedupe chunk_hash for file_chunks (Phase 0.7)
Plain-English:
  - Compute a stable SHA-256 hash per chunk (after normalization).
  - Group rows that resolve to the same hash.
  - Keep one row per hash (oldest by default), delete the others.
  - Set chunk_hash on the kept row if it was NULL.

Usage:
  python -m tools.chunker.migrate_backfill_chunk_hashes --dedupe keep-oldest
Options:
  --dedupe keep-oldest | keep-newest | none   (default: keep-oldest)
"""

from boot.boot_path_initializer import inject_paths
inject_paths()

import argparse
import hashlib
import os
import re
import sqlite3
from typing import Dict, List, Tuple

from core.phase_control import ensure_phase, get_current_phase
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event

REQUIRED_PHASE = 0.7
DB_PATH = "chunk_store.db"

# ----- hashing helpers (match chunker.py normalization) -----

_FRONTMATTER_RE = re.compile(r"^\s*---\s*\n.*?\n---\s*\n", flags=re.DOTALL)

def _strip_frontmatter(text: str) -> str:
    return _FRONTMATTER_RE.sub("", text or "", count=1)

def _normalize_for_hash(text: str) -> str:
    t = _strip_frontmatter(text or "")
    t = t.replace("\r\n", "\n").replace("\r", "\n")
    t = "\n".join(line.rstrip() for line in t.split("\n"))
    return t.strip()

def compute_chunk_hash(text: str) -> str:
    norm = _normalize_for_hash(text)
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()

# ----- core ops -----

def ensure_schema(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS file_chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT,
            chunk_index INTEGER,
            line_start INTEGER,
            line_end INTEGER,
            token_count INTEGER,
            chunk_text TEXT,
            summary TEXT,
            chunk_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cur.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS ux_file_chunks_chunk_hash
        ON file_chunks(chunk_hash)
        WHERE chunk_hash IS NOT NULL;
    """)
    conn.commit()

def load_rows(conn: sqlite3.Connection) -> List[Tuple[int, str, str]]:
    """
    Returns list of (id, chunk_text, chunk_hash) for all rows.
    """
    cur = conn.cursor()
    cur.execute("SELECT id, chunk_text, chunk_hash FROM file_chunks")
    return cur.fetchall()

def plan_groups(rows: List[Tuple[int, str, str]]) -> Dict[str, List[Tuple[int, bool]]]:
    """
    Build groups keyed by the final hash value.
    Each item in a group is (id, has_hash_already).
    """
    groups: Dict[str, List[Tuple[int, bool]]] = {}
    for rid, chunk_text, chunk_hash in rows:
        if chunk_hash:
            h = chunk_hash
            has_hash = True
        else:
            h = compute_chunk_hash(chunk_text or "")
            has_hash = False
        groups.setdefault(h, []).append((rid, has_hash))
    return groups

def apply_groups(conn: sqlite3.Connection, groups: Dict[str, List[Tuple[int, bool]]], mode: str) -> Tuple[int, int]:
    """
    For each hash group, keep exactly one row and delete the rest.
    Also ensure the kept row has chunk_hash set.
    Returns (backfilled_count, deleted_count).
    """
    backfilled = 0
    deleted = 0
    cur = conn.cursor()

    for h, entries in groups.items():
        # Choose which id to keep
        ids = sorted([rid for rid, _ in entries])
        keep_id = ids[0] if mode == "keep-oldest" else ids[-1]

        # Delete all others
        to_delete = [rid for rid, _ in entries if rid != keep_id]
        if to_delete:
            cur.execute(f"DELETE FROM file_chunks WHERE id IN ({','.join('?'*len(to_delete))})", to_delete)
            deleted += cur.rowcount

        # Ensure kept row has hash set
        cur.execute("SELECT chunk_hash FROM file_chunks WHERE id = ?", (keep_id,))
        current = cur.fetchone()
        has_hash_now = bool(current and current[0])
        if not has_hash_now:
            cur.execute("UPDATE file_chunks SET chunk_hash = ? WHERE id = ?", (h, keep_id))
            backfilled += 1

    conn.commit()
    return backfilled, deleted

# ----- runner -----

def run_migration(dedupe_mode: str) -> None:
    ensure_phase(REQUIRED_PHASE)

    if not os.path.exists(DB_PATH):
        print(f"❌ No DB found at {DB_PATH}. Run the chunker first.")
        return

    conn = sqlite3.connect(DB_PATH)
    ensure_schema(conn)

    rows = load_rows(conn)
    groups = plan_groups(rows)
    backfilled, removed = apply_groups(conn, groups, dedupe_mode)

    conn.close()

    # logs
    log_memory_event(
        "migrate_backfill_chunk_hashes complete",
        source=__file__, phase=REQUIRED_PHASE,
        tags=["chunker", "migration"],
    )
    log_trace_event(
        "migrate_backfill_chunk_hashes complete",
        source=__file__, phase=REQUIRED_PHASE,
        tags=["chunker", "migration"],
        content=f"backfilled={backfilled}, removed_dupes={removed}, mode={dedupe_mode}"
    )

    print(f"✅ Backfill complete — hashes set: {backfilled}, duplicates removed: {removed}, mode={dedupe_mode}")

def run_cli():
    parser = argparse.ArgumentParser(description="Backfill and dedupe chunk_hash values in chunk_store.db")
    parser.add_argument("--dedupe", choices=["keep-oldest", "keep-newest", "none"], default="keep-oldest")
    args = parser.parse_args()
    run_migration(args.dedupe)

if __name__ == "__main__":
    run_cli()

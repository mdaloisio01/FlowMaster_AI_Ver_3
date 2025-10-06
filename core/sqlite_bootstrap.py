# === IronRoot Phase Guard (auto-injected) ===
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from boot.boot_path_initializer import inject_paths
inject_paths()
from core.phase_control import ensure_phase
REQUIRED_PHASE = 0.7
ensure_phase(REQUIRED_PHASE)
# === /IronRoot Phase Guard ===

# /core/sqlite_bootstrap.py
"""
SQLite Bootstrap — Will's DB Schema & Initialization (Phase 0.7)
Purpose:
  - Define and migrate the schema used by Will (including chunker storage).
  - Add a de-duplication hash for chunks and enforce uniqueness.
Phase: 0.7 (IronSpine locked)
"""

from boot.boot_path_initializer import inject_paths
inject_paths()

import os
import sqlite3
from typing import Set, Tuple

from core.memory_interface import log_memory_event

# Unify on the chunker DB so all tools read/write the same store.
DB_PATH = "chunk_store.db"


def _table_info(cursor, table: str) -> Set[str]:
    cursor.execute(f"PRAGMA table_info({table});")
    return {row[1] for row in cursor.fetchall()}  # column name is index 1


def _index_names(cursor) -> Set[str]:
    cursor.execute("PRAGMA index_list(file_chunks);")
    # row[1] is the index name
    return {row[1] for row in cursor.fetchall()}


def initialize_database() -> None:
    """
    Create base tables if missing and run safe migrations for Phase 0.7.
    - Ensures file_chunks exists.
    - Ensures chunk_hash column exists.
    - Adds a UNIQUE index on chunk_hash (ignoring NULL values).
    """
    os.makedirs(os.path.dirname(DB_PATH) if os.path.dirname(DB_PATH) else ".", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Base table — file chunk storage (created if missing).
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS file_chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT,
            chunk_index INTEGER,
            line_start INTEGER,
            line_end INTEGER,
            token_count INTEGER,
            chunk_text TEXT,
            summary TEXT,
            chunk_hash TEXT,                   -- Phase 0.7: de-dupe key (normalized SHA-256)
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    # Migrate existing table to include chunk_hash if it doesn't exist.
    existing_cols = _table_info(cursor, "file_chunks")
    if "chunk_hash" not in existing_cols:
        cursor.execute("ALTER TABLE file_chunks ADD COLUMN chunk_hash TEXT;")

    # Add a UNIQUE index on chunk_hash, but only for non-NULL values to avoid
    # blocking older rows that don't have hashes yet. New inserts must set it.
    idx_names = _index_names(cursor)
    if "ux_file_chunks_chunk_hash" not in idx_names:
        cursor.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS ux_file_chunks_chunk_hash
            ON file_chunks(chunk_hash)
            WHERE chunk_hash IS NOT NULL;
            """
        )

    conn.commit()
    conn.close()

    # Memory log so compliance tools can verify bootstrap ran.
    log_memory_event("Bootstrapping Will's DB (Phase 0.7 schema ready)",
                     source=__file__, phase=0.7)


def get_current_phase() -> float:
    # This file is locked for Phase 0.7 in your current build.
    return 0.7


if __name__ == "__main__":
    initialize_database()

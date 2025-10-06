# /tools/chunker/inspect_chunk_db.py
"""
Purpose: CLI tool to inspect the chunk_store.db for chunk statistics and summaries.
Phase: 0.7
"""

from boot.boot_path_initializer import inject_paths
inject_paths()

import argparse
import sqlite3
import os

from core.phase_control import get_current_phase, ensure_phase
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event

REQUIRED_PHASE = 0.7
DB_PATH = "chunk_store.db"

def inspect_chunks(show_summary=False):
    ensure_phase(REQUIRED_PHASE)

    if not os.path.exists(DB_PATH):
        print(f"❌ No chunk DB found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM file_chunks")
    total_chunks = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT file_path) FROM file_chunks")
    total_files = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(token_count) FROM file_chunks")
    total_tokens = cursor.fetchone()[0]

    print("📊 Chunk DB Stats")
    print(f"   Total Chunks: {total_chunks}")
    print(f"   Total Files:  {total_files}")
    print(f"   Total Tokens: {total_tokens}")

    if show_summary:
        print("\n🧠 Sample Chunk Summaries:")
        cursor.execute("SELECT file_path, chunk_index, summary FROM file_chunks LIMIT 5")
        for file_path, chunk_index, summary in cursor.fetchall():
            print(f"\n📄 {file_path} [chunk {chunk_index}]")
            print(f"🔍 {summary or '(no summary)'}")

    conn.close()

    log_memory_event("inspected chunk DB", source=__file__, phase=REQUIRED_PHASE)
    log_trace_event("inspected chunk_store.db", tags=["chunker_inspect"], source=__file__, phase=REQUIRED_PHASE)


def run_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", action="store_true", help="Show chunk summaries")
    args = parser.parse_args()
    inspect_chunks(show_summary=args.summary)

if __name__ == "__main__":
    run_cli()

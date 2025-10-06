# /tools/chunker/summarize_and_index_reflex.py

"""
Chunk Summarizer Reflex
🔹 Purpose: Summarize each chunk in the file_chunks table and store result in 'summary' column
🔹 Phase: 0.7 (IronSpine locked)
"""

from boot.boot_path_initializer import inject_paths
inject_paths()

import sqlite3
from core.trace_logger import log_trace_event
from core.memory_interface import log_memory_event
from core.phase_control import get_current_phase, ensure_phase

REQUIRED_PHASE = 0.7
DB_PATH = "will_memory.db"


def summarize_text(text):
    """
    Placeholder summarizer.
    Real version can be upgraded to LLM-based.
    For now, it uses the first 3 lines or 300 characters.
    """
    lines = text.strip().split("\n")
    snippet = " ".join(lines[:3])
    return snippet[:300] + "..." if len(snippet) > 300 else snippet


def run_summarization():
    ensure_phase(REQUIRED_PHASE)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, chunk_text FROM file_chunks WHERE summary IS NULL")
    rows = cursor.fetchall()

    updated = 0
    for chunk_id, chunk_text in rows:
        summary = summarize_text(chunk_text)
        cursor.execute("UPDATE file_chunks SET summary = ? WHERE id = ?", (summary, chunk_id))
        updated += 1

    conn.commit()
    conn.close()

    log_memory_event(
        "summarize_and_index_reflex completed",
        source=__file__,
        tags=["chunker", "summarization"],
        phase=REQUIRED_PHASE
    )
    log_trace_event(
        "summarize_and_index_reflex completed",
        source=__file__,
        tags=["chunker", "summarization"],
        phase=REQUIRED_PHASE
    )

    print(f"✅ Summarization complete. Updated {updated} chunks.")


if __name__ == "__main__":
    print(f"✅ Current Phase: {get_current_phase()}")
    run_summarization()

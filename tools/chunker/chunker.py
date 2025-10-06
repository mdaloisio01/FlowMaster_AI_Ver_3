# /tools/chunker/chunker.py
"""
Chunker Engine — Phase 0.7 Token-Safe File Chunker with De-Duplication
Purpose:
  - Walk a directory (or unzip an archive), select text files, and split into token-bounded chunks.
  - Store chunks in SQLite with a normalized SHA-256 'chunk_hash' to prevent duplicates.
  - Optionally export chunks as .txt for human inspection.
Phase: 0.7 (IronSpine locked)
"""

from boot.boot_path_initializer import inject_paths
inject_paths()

import os
import re
import zipfile
import hashlib
import sqlite3
from typing import Iterable, List, Tuple

import tiktoken

from core.phase_control import get_current_phase, ensure_phase
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event

REQUIRED_PHASE = 0.7
ensure_phase(REQUIRED_PHASE)

DB_PATH = "chunk_store.db"
CHUNK_EXPORT_DIR = "chunks"
MAX_TOKENS_PER_CHUNK = 2000

# Allow-list for text-like files
TEXT_EXTS = {".py", ".md", ".txt", ".json", ".yaml", ".yml", ".csv", ".toml", ".ini", ".cfg", ".xml", ".html", ".css", ".js", ".ts"}

tokenizer = tiktoken.get_encoding("cl100k_base")


def unzip_if_needed(path: str) -> str:
    if path.lower().endswith(".zip"):
        extract_path = path[:-4] + "_unzipped"
        with zipfile.ZipFile(path, "r") as zf:
            zf.extractall(extract_path)
        return extract_path
    return path


def is_text_file(file_path: str) -> bool:
    _, ext = os.path.splitext(file_path)
    if ext.lower() in TEXT_EXTS:
        # Skip typical junk folders by path fragments
        lowered = file_path.replace("\\", "/").lower()
        for skip in ("/.git/", "/node_modules/", "/__pycache__/", "/env/", "/venv/"):
            if skip in lowered:
                return False
        return True
    return False


def encode_count(text: str) -> int:
    return len(tokenizer.encode(text))


# --------- Hashing Helpers (de-dupe) ---------

_FRONTMATTER_RE = re.compile(r"^\s*---\s*\n.*?\n---\s*\n", flags=re.DOTALL)


def _strip_frontmatter(text: str) -> str:
    """Remove YAML frontmatter if present at file start (for chat bundles)."""
    return _FRONTMATTER_RE.sub("", text, count=1)


def _normalize_for_hash(text: str) -> str:
    """
    Normalization for stable hashing:
      - drop frontmatter
      - normalize newlines to \n
      - strip outer whitespace
      - collapse trailing spaces on lines
    """
    t = _strip_frontmatter(text)
    t = t.replace("\r\n", "\n").replace("\r", "\n")
    # Remove trailing spaces per line
    t = "\n".join(line.rstrip() for line in t.split("\n"))
    return t.strip()


def compute_chunk_hash(text: str) -> str:
    norm = _normalize_for_hash(text)
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()


# --------- DB Helpers ---------

def _ensure_table(conn: sqlite3.Connection) -> None:
    """Create table if missing (bootstrap also handles this)."""
    cur = conn.cursor()
    cur.execute(
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
            chunk_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    # Unique index on chunk_hash for non-NULL values.
    cur.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS ux_file_chunks_chunk_hash
        ON file_chunks(chunk_hash)
        WHERE chunk_hash IS NOT NULL;
        """
    )
    conn.commit()


def insert_chunk(file_path: str, chunk_index: int, line_start: int, line_end: int,
                 token_count: int, chunk_text: str) -> bool:
    """
    Insert a chunk row. Returns True if inserted, False if skipped due to duplicate.
    """
    conn = sqlite3.connect(DB_PATH)
    _ensure_table(conn)
    cur = conn.cursor()

    c_hash = compute_chunk_hash(chunk_text)

    try:
        # Use OR IGNORE so duplicates (same chunk_hash) are skipped cleanly.
        cur.execute(
            """
            INSERT OR IGNORE INTO file_chunks
            (file_path, chunk_index, line_start, line_end, token_count, chunk_text, chunk_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            (file_path, chunk_index, line_start, line_end, token_count, chunk_text, c_hash),
        )
        conn.commit()
        inserted = cur.rowcount > 0
    finally:
        conn.close()

    return inserted


def write_txt_chunk(file_path: str, chunk_index: int, chunk_text: str) -> None:
    os.makedirs(CHUNK_EXPORT_DIR, exist_ok=True)
    base = os.path.basename(file_path).replace("/", "_").replace("\\", "_")
    out_file = f"{CHUNK_EXPORT_DIR}/{base}_chunk{chunk_index:03d}.txt"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(chunk_text)


# --------- Chunking ---------

def tokenize_lines(lines: List[str]) -> List[int]:
    # We count per-line tokens; chunking packs lines until the limit.
    return [encode_count(line) for line in lines]


def split_into_chunks(lines: List[str]) -> List[Tuple[List[str], int, int, int]]:
    """
    Returns a list of tuples: (chunk_lines, token_count, line_start, line_end).
    line numbers are 1-based.
    """
    token_counts = tokenize_lines(lines)
    chunks: List[Tuple[List[str], int, int, int]] = []

    current_lines: List[str] = []
    current_tokens = 0
    current_start = 1
    line_no = 1

    for line, tcount in zip(lines, token_counts):
        if current_tokens + tcount > MAX_TOKENS_PER_CHUNK and current_lines:
            # finalize current chunk
            chunk_end = line_no - 1
            chunks.append((current_lines, current_tokens, current_start, chunk_end))
            # start new chunk
            current_lines = []
            current_tokens = 0
            current_start = line_no

        current_lines.append(line)
        current_tokens += tcount
        line_no += 1

    if current_lines:
        chunk_end = line_no - 1
        chunks.append((current_lines, current_tokens, current_start, chunk_end))

    return chunks


# --------- Runner ---------

def run_chunker(input_path: str, write_txt: bool = True) -> None:
    ensure_phase(REQUIRED_PHASE)

    log_memory_event("chunker_run_start", source=__file__, phase=REQUIRED_PHASE,
                     tags=["chunker", "start"])
    log_trace_event("chunker_run_start", source=__file__, phase=REQUIRED_PHASE,
                    tags=["chunker", "start"], content=f"Input: {input_path}")

    root_path = unzip_if_needed(input_path)

    total_files = 0
    total_chunks = 0
    total_inserted = 0
    total_skipped_dupes = 0

    for dirpath, _, filenames in os.walk(root_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if not is_text_file(file_path):
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
            except Exception as e:
                log_trace_event("chunker_file_read_error", source=__file__, phase=REQUIRED_PHASE,
                                tags=["chunker", "error"], content=f"{file_path}: {e}")
                continue

            total_files += 1
            chunk_sets = split_into_chunks(lines)
            total_chunks += len(chunk_sets)

            for idx, (chunk_lines, token_count, line_start, line_end) in enumerate(chunk_sets):
                text = "".join(chunk_lines)
                inserted = insert_chunk(file_path, idx, line_start, line_end, token_count, text)
                if inserted:
                    total_inserted += 1
                    if write_txt:
                        write_txt_chunk(file_path, idx, text)
                else:
                    total_skipped_dupes += 1

    log_trace_event(
        "chunker_run_complete",
        source=__file__,
        phase=REQUIRED_PHASE,
        tags=["chunker", "done"],
        content=f"files={total_files}, chunks={total_chunks}, inserted={total_inserted}, dupes_skipped={total_skipped_dupes}"
    )
    log_memory_event(
        "chunker_run_complete",
        source=__file__,
        phase=REQUIRED_PHASE,
        tags=["chunker", "done"]
    )

    print(
        f"✅ Chunker complete — files={total_files}, chunks={total_chunks}, "
        f"inserted={total_inserted}, dupes_skipped={total_skipped_dupes}"
    )


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        run_chunker(sys.argv[1])
    else:
        print("Usage: python -m tools.chunker.chunker <input_dir_or_zip>")

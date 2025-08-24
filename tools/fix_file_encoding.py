# tools/fix_file_encoding.py
from __future__ import annotations

from boot.boot_path_initializer import inject_paths
inject_paths()

import argparse
from pathlib import Path

from core.phase_control import REQUIRED_PHASE, ensure_phase
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event


def _is_text_file(p: Path) -> bool:
    return p.suffix in {".py", ".md", ".json", ".yaml", ".yml", ".txt"}


def run_cli() -> None:
    ensure_phase()
    tool_name = Path(__file__).as_posix()

    parser = argparse.ArgumentParser(description="Normalize file encodings to UTF-8.")
    parser.add_argument("--write", action="store_true", help="Actually rewrite files as UTF-8")
    parser.add_argument("--root", default=".", help="Root directory to scan")
    args = parser.parse_args()

    # Normalize incoming path arg
    root = Path((args.root or ".").replace("\\", "/"))

    log_memory_event(
        f"fix_file_encoding start (write={args.write}, root={root.as_posix()})",
        source=tool_name,
        tags=["tool", "start", "fix_file_encoding"],
        content="starting",
        phase=REQUIRED_PHASE,
    )

    scanned = 0
    fixed = 0
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if not _is_text_file(p):
            continue
        scanned += 1
        try:
            p.read_text(encoding="utf-8")
        except Exception:
            if args.write:
                raw = p.read_bytes()
                try:
                    txt = raw.decode("utf-8", errors="replace")
                    p.write_text(txt, encoding="utf-8")
                    fixed += 1
                except Exception:
                    pass

    print(f"Scanned: {scanned} files; Fixed: {fixed} files (write={args.write})")

    log_trace_event(
        "fix_file_encoding done",
        source=tool_name,
        tags=["tool", "done", "fix_file_encoding"],
        phase=REQUIRED_PHASE,
    )


if __name__ == "__main__":
    run_cli()

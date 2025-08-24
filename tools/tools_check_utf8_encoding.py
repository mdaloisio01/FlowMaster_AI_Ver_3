from __future__ import annotations
from boot.boot_path_initializer import inject_paths
inject_paths()

import argparse
from pathlib import Path
from typing import List

from core.phase_control import ensure_phase, REQUIRED_PHASE
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event


def _is_utf8(p: Path) -> bool:
    try:
        _ = p.read_text(encoding="utf-8")
        return True
    except Exception:
        return False


def run_cli() -> None:
    ensure_phase()
    src = Path(__file__).as_posix()

    parser = argparse.ArgumentParser(description="Verify repository text files are UTF-8.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--exts", nargs="*", default=[".py", ".md", ".json", ".yaml", ".yml", ".txt"])
    args = parser.parse_args()

    log_memory_event(
        event_text="tools_check_utf8_encoding start",
        source=src,
        tags=["tool", "start", "utf8_check"],
        content={"root": args.root, "exts": args.exts},
        phase=REQUIRED_PHASE,
    )

    root = Path(args.root)
    scanned = 0
    bad: List[str] = []
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in {e.lower() for e in args.exts}:
            scanned += 1
            if not _is_utf8(p):
                bad.append(p.as_posix())

    if bad:
        print(f"❌ Non-UTF8 files ({len(bad)}):")
        for b in bad[:100]:
            print("  -", b)
    else:
        print(f"✅ UTF-8 check ok across {scanned} files")

    log_trace_event(
        description="tools_check_utf8_encoding done",
        source=src,
        tags=["tool", "done", "utf8_check"],
        content={"scanned": scanned, "non_utf8": bad[:50]},
        phase=REQUIRED_PHASE,
    )


if __name__ == "__main__":
    run_cli()

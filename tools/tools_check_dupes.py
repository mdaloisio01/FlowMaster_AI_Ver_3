from __future__ import annotations
from boot.boot_path_initializer import inject_paths
inject_paths()

import argparse
from collections import Counter
from pathlib import Path

from core.phase_control import ensure_phase, REQUIRED_PHASE
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event


def run_cli() -> None:
    ensure_phase()
    src = Path(__file__).as_posix()

    parser = argparse.ArgumentParser(description="Detect duplicate lines in dev_file_list.md")
    parser.add_argument("--dev", default="configs/dev_file_list.md")
    args = parser.parse_args()

    log_memory_event(
        event_text="tools_check_dupes start",
        source=src,
        tags=["tool", "start", "dupes"],
        content={"dev": args.dev},
        phase=REQUIRED_PHASE,
    )

    p = Path(args.dev)
    lines = [ln.strip() for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()]
    dupes = [item for item, cnt in Counter(lines).items() if cnt > 1]

    if dupes:
        print(f"Found {len(dupes)} duplicates:")
        for d in sorted(dupes):
            print("  *", d)
    else:
        print("No duplicates.")

    log_trace_event(
        description="tools_check_dupes done",
        source=src,
        tags=["tool", "done", "dupes"],
        content={"dupes": sorted(dupes)},
        phase=REQUIRED_PHASE,
    )


if __name__ == "__main__":
    run_cli()

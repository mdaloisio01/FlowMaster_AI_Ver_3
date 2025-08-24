from __future__ import annotations
from boot.boot_path_initializer import inject_paths
inject_paths()

import argparse
from pathlib import Path

from core.phase_control import ensure_phase, REQUIRED_PHASE, get_current_phase
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event


def run_cli() -> None:
    ensure_phase()
    src = Path(__file__).as_posix()

    parser = argparse.ArgumentParser(description="Emit a test memory + trace event.")
    parser.add_argument("--text", default="test memory log", help="Event text for memory log.")
    args = parser.parse_args()

    log_memory_event(
        event_text=args.text,
        source=src,
        tags=["tool", "test", "memory_logger"],
        content={"current_phase": get_current_phase()},
        phase=REQUIRED_PHASE,
    )
    log_trace_event(
        description="test_memory_logger done",
        source=src,
        tags=["tool", "done", "memory_logger"],
        content={"ok": True},
        phase=REQUIRED_PHASE,
    )
    print("✅ test_memory_logger wrote memory + trace events")


if __name__ == "__main__":
    run_cli()

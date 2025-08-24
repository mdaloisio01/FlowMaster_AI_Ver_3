# tools/print_current_phase.py
from __future__ import annotations

from boot.boot_path_initializer import inject_paths
inject_paths()

from pathlib import Path

from core.phase_control import REQUIRED_PHASE, get_current_phase, ensure_phase
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event


def run_cli() -> None:
    ensure_phase()
    tool_name = Path(__file__).as_posix()

    log_memory_event(
        "print_current_phase start",
        source=tool_name,
        tags=["tool", "start", "print_current_phase"],
        content="starting",
        phase=REQUIRED_PHASE,
    )

    cur = get_current_phase()
    print(f"Current phase: {cur}")

    log_trace_event(
        "print_current_phase done",
        source=tool_name,
        tags=["tool", "done", "print_current_phase"],
        phase=REQUIRED_PHASE,
    )


if __name__ == "__main__":
    run_cli()

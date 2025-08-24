# Path injection must be first
from boot.boot_path_initializer import inject_paths
inject_paths()

import sys
from pathlib import Path

from core.phase_control import REQUIRED_PHASE, get_current_phase, ensure_phase
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event


def run_cli() -> None:
    # Start log (memory)
    log_memory_event(
        event_text="tests: phase_0_integrity start",
        source=__name__,
        tags=["test", "start", "phase0"],
        content={"cwd": Path(".").as_posix()},
        phase=REQUIRED_PHASE,
    )

    # Assertions
    ensure_phase()  # should not raise
    assert isinstance(REQUIRED_PHASE, float) or isinstance(REQUIRED_PHASE, (int,)), "REQUIRED_PHASE should be numeric"
    assert get_current_phase() == REQUIRED_PHASE, "current phase must equal REQUIRED_PHASE"

    # Done log (trace)
    log_trace_event(
        description="tests: phase_0_integrity done",
        source=__name__,
        tags=["test", "done", "phase0"],
        content={"required_phase": REQUIRED_PHASE, "current_phase": get_current_phase()},
        phase=REQUIRED_PHASE,
    )
    print("✅ phase_0_integrity ok")


if __name__ == "__main__":
    run_cli()

from __future__ import annotations
from boot.boot_path_initializer import inject_paths
inject_paths()

from pathlib import Path
from core.phase_control import ensure_phase, REQUIRED_PHASE, get_current_phase
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event


def run_cli() -> None:
    ensure_phase()
    src = Path(__file__).as_posix()
    log_memory_event(
        event_text="reflex_core package entry",
        source=src,
        tags=["reflex", "package", "start"],
        content={"current_phase": get_current_phase(), "required_phase": REQUIRED_PHASE},
        phase=REQUIRED_PHASE,
    )
    log_trace_event(
        description="reflex_core package entry done",
        source=src,
        tags=["reflex", "package", "done"],
        content="ok",
        phase=REQUIRED_PHASE,
    )
    print("reflex_core package: available reflexes -> reflex_trace_ping, reflex_loader, reflex_self_test_runner")


if __name__ == "__main__":
    run_cli()

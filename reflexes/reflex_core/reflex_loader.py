# reflexes/reflex_core/reflex_loader.py
from __future__ import annotations

from boot.boot_path_initializer import inject_paths
inject_paths()

from pathlib import Path

from core.phase_control import REQUIRED_PHASE, ensure_phase
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event


def run_cli() -> None:
    ensure_phase()
    mod_name = Path(__file__).as_posix()

    log_memory_event(
        "reflex_loader start",
        source=mod_name,
        tags=["reflex", "start", "reflex_loader"],
        content="loading_reflexes",
        phase=REQUIRED_PHASE,
    )

    print("Reflex loader: OK (Phase 0.4 instrumentation active)")

    log_trace_event(
        "reflex_loader done",
        source=mod_name,
        tags=["reflex", "done", "reflex_loader"],
        phase=REQUIRED_PHASE,
    )


if __name__ == "__main__":
    run_cli()

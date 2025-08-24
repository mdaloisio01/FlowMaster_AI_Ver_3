# Path injection must be first
from boot.boot_path_initializer import inject_paths
inject_paths()

import importlib
from pathlib import Path

from core.phase_control import REQUIRED_PHASE, ensure_phase
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event


def _try_run_trace_ping() -> None:
    """
    Import reflexes.reflex_core.reflex_trace_ping and invoke run_cli() if present.
    This mirrors the manual `py -m reflexes.reflex_core.reflex_trace_ping` check.
    """
    mod = importlib.import_module("reflexes.reflex_core.reflex_trace_ping")
    fn = getattr(mod, "run_cli", None)
    if callable(fn):
        fn()  # should print a success line and emit logs
    else:
        # If no explicit CLI, import is still a pass for this phase.
        pass


def run_cli() -> None:
    ensure_phase()

    log_memory_event(
        event_text="tests: phase_0_3_integrity start",
        source=__name__,
        tags=["test", "start", "phase0_3"],
        content={},
        phase=REQUIRED_PHASE,
    )

    # Reflex ping should import and run without raising
    _try_run_trace_ping()

    log_trace_event(
        description="tests: phase_0_3_integrity done",
        source=__name__,
        tags=["test", "done", "phase0_3"],
        content={},
        phase=REQUIRED_PHASE,
    )
    print("✅ phase_0_3_integrity ok")


if __name__ == "__main__":
    run_cli()

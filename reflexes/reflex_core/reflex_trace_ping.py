# reflexes/reflex_core/reflex_trace_ping.py
# Canonical Reflex Template (Phase-locked, dual logging, path injection)

from boot.boot_path_initializer import inject_paths
inject_paths()

from core.phase_control import ensure_phase, REQUIRED_PHASE
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event

def run_cli():
    ensure_phase()  # fail-closed if not REQUIRED_PHASE

    # Dual logging: memory + trace
    log_memory_event(
        event_text="reflex_trace_ping memory",
        source=__file__.replace("\\", "/"),
        tags=["reflex", "test", "trace"],
        content={"msg": "ping"},
        phase=REQUIRED_PHASE,
    )
    log_trace_event(
        description="reflex_trace_ping executed",
        source=__file__.replace("\\", "/"),
        tags=["reflex", "test", "trace"],
        content={"result": "ok"},
        phase=REQUIRED_PHASE,
    )

    print("✅ trace_ping ok")

if __name__ == "__main__":
    run_cli()

# /reflexes/reflex_core/<your_reflex_name>.py
"""
Reflex: <your_reflex_name>
Phase: <REQUIRED_PHASE_INT>
Purpose: <one-line purpose>
"""

from boot.boot_path_initializer import inject_paths
inject_paths()

from configs.ironroot_manifest_loader import get_current_phase
from core.memory_log_db import log_memory_event
from core.trace_logger import log_trace_event

REQUIRED_PHASE = <REQUIRED_PHASE_INT>

def run(**kwargs):
    # Phase lock
    if get_current_phase() < REQUIRED_PHASE:
        raise RuntimeError("❌ Not allowed in this phase")

    # Your reflex logic here...
    result = {"status": "ok", "details": "replace with real logic"}

    # Dual logging (memory + trace)
    log_memory_event(
        event_type="reflex_run",
        phase=REQUIRED_PHASE,
        source=__name__,
        metadata={"kwargs": kwargs, "result": result},
    )
    log_trace_event(
        event_type="reflex_run",
        reflex=__name__,
        source=__name__,
        tags=["reflex", "<your_tag>"],
        metadata={"kwargs": kwargs, "result": result},
    )
    return result

if __name__ == "__main__":
    print(run())

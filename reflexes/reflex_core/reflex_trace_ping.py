from __future__ import annotations
# reflexes/reflex_core/reflex_trace_ping.py — simple ping reflex

import sys
from pathlib import Path

# Ensure repo root on path (…/reflexes/reflex_core -> repo root)
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from boot import boot_path_initializer as bpi
bpi.inject_paths()

from core.trace_logger import log_trace_event, log_memory_event
from core.phase_control import get_current_phase

def run_cli() -> None:
    phase = get_current_phase()

    # Start trace
    log_trace_event(
        "reflex_trace_ping.start",
        {"message": "ping starting"},
        source="reflexes.reflex_core.reflex_trace_ping",
        phase=phase,
    )

    # Optional: write a tiny memory event too
    log_memory_event(
        "reflex_trace_ping",
        {"ok": True},
        source="reflexes.reflex_core.reflex_trace_ping",
        phase=phase,
    )

    # End trace
    log_trace_event(
        "reflex_trace_ping.done",
        {"message": "ping complete"},
        source="reflexes.reflex_core.reflex_trace_ping",
        phase=phase,
    )

if __name__ == "__main__":
    run_cli()

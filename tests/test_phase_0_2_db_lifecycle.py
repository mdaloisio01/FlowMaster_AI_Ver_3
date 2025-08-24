# Path injection must be first
from boot.boot_path_initializer import inject_paths
inject_paths()

from pathlib import Path
import time
import json

from core.phase_control import REQUIRED_PHASE, ensure_phase
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event


MEM_LOG = Path("logs/will_memory_log.json")
TRACE_LOG = Path("logs/reflex_trace_log.json")


def _safe_count_lines(p: Path) -> int:
    if not p.exists():
        return 0
    try:
        return sum(1 for _ in p.open("r", encoding="utf-8", errors="ignore"))
    except Exception:
        return 0


def run_cli() -> None:
    ensure_phase()

    # Baseline counts
    mem_before = _safe_count_lines(MEM_LOG)
    trace_before = _safe_count_lines(TRACE_LOG)

    log_memory_event(
        event_text="tests: db_lifecycle start",
        source=__name__,
        tags=["test", "start", "db_lifecycle"],
        content={"mem_before": mem_before, "trace_before": trace_before},
        phase=REQUIRED_PHASE,
    )

    # Emit one memory + one trace entry and verify the line counts increase.
    log_memory_event(
        event_text="db_lifecycle probe memory",
        source=__name__,
        tags=["test", "probe", "db_lifecycle"],
        content={"ts": time.time()},
        phase=REQUIRED_PHASE,
    )
    log_trace_event(
        description="db_lifecycle probe trace",
        source=__name__,
        tags=["test", "probe", "db_lifecycle"],
        content={"ts": time.time()},
        phase=REQUIRED_PHASE,
    )

    # Re-count
    mem_after = _safe_count_lines(MEM_LOG)
    trace_after = _safe_count_lines(TRACE_LOG)

    assert mem_after >= mem_before + 1, f"Memory log did not grow: before={mem_before} after={mem_after}"
    assert trace_after >= trace_before + 1, f"Trace log did not grow: before={trace_before} after={trace_after}"

    log_trace_event(
        description="tests: db_lifecycle done",
        source=__name__,
        tags=["test", "done", "db_lifecycle"],
        content={"mem_after": mem_after, "trace_after": trace_after},
        phase=REQUIRED_PHASE,
    )
    print("✅ db_lifecycle ok")


if __name__ == "__main__":
    run_cli()

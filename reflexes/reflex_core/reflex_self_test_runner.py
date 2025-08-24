from __future__ import annotations
from boot.boot_path_initializer import inject_paths
inject_paths()

import argparse
from pathlib import Path
from typing import Dict, Any, List

from core.phase_control import ensure_phase, REQUIRED_PHASE, get_current_phase
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event


def _run_subtests() -> Dict[str, Any]:
    """
    Minimal, deterministic self-tests for reflexes.
    Currently invokes trace_ping and reports success.
    """
    # Import lazily to avoid side-effects on import
    from reflexes.reflex_core.reflex_trace_ping import run_cli as _ping

    # Capture output by invoking the ping reflex
    try:
        _ping()
        return {"trace_ping": "ok"}
    except Exception as e:
        return {"trace_ping": f"error: {e!r}"}


def run_cli() -> None:
    ensure_phase()
    src = Path(__file__).as_posix()

    parser = argparse.ArgumentParser(description="Reflex self-test runner (Phase 0.4)")
    _ = parser.parse_args()

    log_memory_event(
        event_text="reflex_self_test_runner start",
        source=src,
        tags=["reflex", "start", "self_test"],
        content={"current_phase": get_current_phase()},
        phase=REQUIRED_PHASE,
    )

    summary = _run_subtests()
    ok = all(v == "ok" for v in summary.values())
    if ok:
        print("✅ reflex_self_test_runner: all subtests ok")
    else:
        print("❌ reflex_self_test_runner failures:", summary)

    log_trace_event(
        description="reflex_self_test_runner done",
        source=src,
        tags=["reflex", "done", "self_test"],
        content=summary,
        phase=REQUIRED_PHASE,
    )


if __name__ == "__main__":
    run_cli()

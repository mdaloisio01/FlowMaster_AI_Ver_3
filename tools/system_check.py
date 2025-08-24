# tools/system_check.py
from __future__ import annotations

from boot.boot_path_initializer import inject_paths
inject_paths()

from pathlib import Path

from core.phase_control import REQUIRED_PHASE, ensure_phase
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event


def run_cli() -> None:
    ensure_phase()
    tool_name = Path(__file__).as_posix()

    log_memory_event(
        "system_check start",
        source=tool_name,
        tags=["tool", "start", "system_check"],
        content="starting",
        phase=REQUIRED_PHASE,
    )

    required = [
        Path("logs/will_memory_log.json"),
        Path("logs/reflex_trace_log.json"),
        Path("core/phase_control.py"),
    ]
    missing = [p.as_posix() for p in required if not p.exists()]
    if missing:
        print("Missing required files:")
        for m in missing:
            print(f" - {m}")
    else:
        print("System check: OK")

    log_trace_event(
        "system_check done",
        source=tool_name,
        tags=["tool", "done", "system_check"],
        phase=REQUIRED_PHASE,
    )

    if missing:
        raise SystemExit(3)


if __name__ == "__main__":
    run_cli()

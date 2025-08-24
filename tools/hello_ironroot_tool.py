# tools/hello_ironroot_tool.py
# Minimal compliant CLI tool for IronRoot:
# - Path injection first
# - Phase lock (ensure_phase + explicit check)
# - Dual logging (memory + trace)
# - Canonical run_cli() + main guard
# - No business logic; prints a friendly line

from boot.boot_path_initializer import inject_paths
inject_paths()

import argparse
from pathlib import Path

from core.phase_control import ensure_phase, REQUIRED_PHASE
from core.phase_control import get_current_phase
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event


def run_cli() -> None:
    # Phase enforcement
    ensure_phase()
    current_phase = get_current_phase()
    if current_phase != REQUIRED_PHASE:
        raise RuntimeError(f"IRONROOT VIOLATION ? Phase mismatch. Required: {REQUIRED_PHASE}, Current: {current_phase}")

    parser = argparse.ArgumentParser(description="Hello IronRoot tool")
    parser.add_argument("--message", default="hello_ironroot ok", help="Message to print")
    args = parser.parse_args()

    src = Path(__file__).as_posix()
    log_memory_event("hello_ironroot start", source=src, tags=["tool", "probe"], content={"msg": args.message}, phase=REQUIRED_PHASE)
    log_trace_event("hello_ironroot start", source=src, tags=["tool", "probe"], content={"msg": args.message}, phase=REQUIRED_PHASE)

    print(args.message)

    log_memory_event("hello_ironroot done", source=src, tags=["tool", "probe"], content={"msg": args.message}, phase=REQUIRED_PHASE)
    log_trace_event("hello_ironroot done", source=src, tags=["tool", "probe"], content={"msg": args.message}, phase=REQUIRED_PHASE)


if __name__ == "__main__":
    run_cli()

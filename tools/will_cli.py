from __future__ import annotations
from boot.boot_path_initializer import inject_paths
inject_paths()

import argparse
from pathlib import Path

from core.phase_control import ensure_phase, REQUIRED_PHASE
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event


def run_cli() -> None:
    ensure_phase()
    src = Path(__file__).as_posix()

    parser = argparse.ArgumentParser(prog="will", description="Will CLI dispatcher (Phase 0.4)")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("ping", help="Run reflex_trace_ping")
    sub.add_parser("boot", help="Run boot loader")

    args = parser.parse_args()

    log_memory_event(
        event_text="will_cli start",
        source=src,
        tags=["tool", "start", "will_cli"],
        content={"cmd": args.cmd},
        phase=REQUIRED_PHASE,
    )

    if args.cmd == "ping":
        from reflexes.reflex_core.reflex_trace_ping import run_cli as _ping
        _ping()
    elif args.cmd == "boot":
        from boot.boot_phase_loader import run_cli as _boot
        _boot()
    else:
        parser.print_help()

    log_trace_event(
        description="will_cli done",
        source=src,
        tags=["tool", "done", "will_cli"],
        content={"cmd": args.cmd or "help"},
        phase=REQUIRED_PHASE,
    )


if __name__ == "__main__":
    run_cli()

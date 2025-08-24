# Canonical_CLI_Tool_Template.py
# A minimal, runnable CLI tool template for FlowMaster AI.
# - Uses phase enforcement from core.phase_control
# - Logs both memory + trace events
# - Works cross-platform (forward slashes)
#
# Usage:
#   python -m Canonical_CLI_Tool_Template --message "hello"

from boot.boot_path_initializer import inject_paths
inject_paths()

from __future__ import annotations

import argparse
from pathlib import Path

from core.phase_control import REQUIRED_PHASE, ensure_phase, get_current_phase
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event


def run_cli() -> None:
    ensure_phase()
    tool = Path(__file__).as_posix()

    parser = argparse.ArgumentParser(
        description="Canonical CLI Tool Template (Phase 0.4-compliant)."
    )
    parser.add_argument("--message", default="ok", help="Message to echo for smoke-test.")
    args = parser.parse_args()

    log_memory_event(
        event_text="canonical_cli_template start",
        source=tool,
        tags=["tool", "start", "canonical"],
        content={"current_phase": get_current_phase(), "message": args.message},
        phase=REQUIRED_PHASE,
    )

    print(f"[Canonical CLI] message: {args.message}")

    log_trace_event(
        description="canonical_cli_template done",
        source=tool,
        tags=["tool", "done", "canonical"],
        content={"result": "success"},
        phase=REQUIRED_PHASE,
    )


if __name__ == "__main__":
    run_cli()

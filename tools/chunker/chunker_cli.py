# /tools/chunker/chunker_cli.py

"""
CLI Interface — Will's Chunker Engine Trigger
🔹 Purpose: Simple CLI wrapper to run chunker.py with correct args
🔹 Phase: 0.7 (Locked under IronSpine)
"""

from boot.boot_path_initializer import inject_paths
inject_paths()

import argparse
from core.phase_control import get_current_phase, ensure_phase
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event
from tools.chunker.chunker import run_chunker

REQUIRED_PHASE = 0.7
ensure_phase(REQUIRED_PHASE)


def run_cli():
    parser = argparse.ArgumentParser(description="Will's Token-Bound Chunker CLI")
    parser.add_argument("input_path", help="Path to a folder or .zip file to chunk")
    parser.add_argument("--no-txt", action="store_true", help="Disable .txt chunk exports")
    args = parser.parse_args()

    log_memory_event("chunker_cli run", source="tools/chunker/chunker_cli.py")
    log_trace_event("chunker_cli run", tags=["cli", "chunker"], content=f"Input: {args.input_path}")

    run_chunker(args.input_path, write_txt=not args.no_txt)


if __name__ == "__main__":
    run_cli()

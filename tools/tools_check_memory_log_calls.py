from __future__ import annotations
from boot.boot_path_initializer import inject_paths
inject_paths()

import argparse
from pathlib import Path
from typing import List, Tuple

from core.phase_control import ensure_phase, REQUIRED_PHASE
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event


def _scan_file(p: Path) -> Tuple[bool, bool]:
    """
    Returns (has_memory_log_call, has_trace_log_call)
    """
    try:
        text = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return (False, False)
    return ("log_memory_event(" in text, "log_trace_event(" in text)


def run_cli() -> None:
    ensure_phase()
    src = Path(__file__).as_posix()

    parser = argparse.ArgumentParser(description="Scan .py files for memory/trace logging calls.")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    log_memory_event(
        event_text="tools_check_memory_log_calls start",
        source=src,
        tags=["tool", "start", "scan_logs"],
        content={"root": args.root},
        phase=REQUIRED_PHASE,
    )

    root = Path(args.root)
    scanned = 0
    missing_mem: List[str] = []
    missing_trace: List[str] = []

    for p in root.rglob("*.py"):
        if any(part in {"__pycache__", ".venv", "venv"} for part in p.parts):
            continue
        scanned += 1
        has_mem, has_trace = _scan_file(p)
        if not has_mem:
            missing_mem.append(p.as_posix())
        if not has_trace:
            missing_trace.append(p.as_posix())

    print(f"Scanned {scanned} files")
    print(f"Files missing log_memory_event: {len(missing_mem)}")
    print(f"Files missing log_trace_event: {len(missing_trace)}")

    log_trace_event(
        description="tools_check_memory_log_calls done",
        source=src,
        tags=["tool", "done", "scan_logs"],
        content={
            "scanned": scanned,
            "missing_memory": missing_mem[:50],
            "missing_trace": missing_trace[:50],
        },
        phase=REQUIRED_PHASE,
    )


if __name__ == "__main__":
    run_cli()

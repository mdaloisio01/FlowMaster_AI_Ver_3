from __future__ import annotations
from boot.boot_path_initializer import inject_paths
inject_paths()

import argparse
import ast
from pathlib import Path

from core.phase_control import ensure_phase, REQUIRED_PHASE
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event


def _has_phase_enforcement(py_code: str) -> bool:
    try:
        tree = ast.parse(py_code)
    except Exception:
        return False
    text = py_code
    return ("from core.phase_control import" in text) and ("ensure_phase" in text or "REQUIRED_PHASE" in text)


def run_cli() -> None:
    ensure_phase()
    src = Path(__file__).as_posix()
    parser = argparse.ArgumentParser(description="Sweep repository for phase enforcement markers.")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    log_memory_event(
        event_text="phase_guard_sweep start",
        source=src,
        tags=["tool", "start", "phase_guard_sweep"],
        content={"root": args.root},
        phase=REQUIRED_PHASE,
    )

    root = Path(args.root)
    scanned, missing = 0, []
    for p in root.rglob("*.py"):
        if any(part in {"__pycache__", ".venv", "venv"} for part in p.parts):
            continue
        code = p.read_text(encoding="utf-8", errors="ignore")
        scanned += 1
        if not _has_phase_enforcement(code):
            missing.append(p.as_posix())

    print(f"Scanned: {scanned} files; Missing enforcement: {len(missing)}")
    for m in missing[:100]:
        print("  -", m)

    log_trace_event(
        description="phase_guard_sweep done",
        source=src,
        tags=["tool", "done", "phase_guard_sweep"],
        content={"scanned": scanned, "missing": missing[:50]},
        phase=REQUIRED_PHASE,
    )


if __name__ == "__main__":
    run_cli()

# tools/manifest_sync.py
from __future__ import annotations

from boot.boot_path_initializer import inject_paths
inject_paths()

import json
from pathlib import Path
from typing import List

from core.phase_control import REQUIRED_PHASE, ensure_phase
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event


DEV_LIST = Path("configs/dev_file_list.md")
MANIFEST = Path("configs/ironroot_manifest_data.json")


def _read_list() -> List[str]:
    if not DEV_LIST.exists():
        return []
    lines = [ln.strip() for ln in DEV_LIST.read_text(encoding="utf-8").splitlines()]
    # Normalize any backslashes that might sneak in
    return [ln.replace("\\", "/") for ln in lines if ln and not ln.startswith("#")]


def run_cli() -> None:
    ensure_phase()
    tool_name = Path(__file__).as_posix()

    log_memory_event(
        "manifest_sync start",
        source=tool_name,
        tags=["tool", "start", "manifest_sync"],
        content="starting",
        phase=REQUIRED_PHASE,
    )

    files = _read_list()
    if not files:
        print("No files found in dev_file_list.md")
        raise SystemExit(5)

    manifest_data = {
        "current_phase": REQUIRED_PHASE,
        "manifest": {},
        "files": files,
    }
    print(f"Manifest dry-run: {len(files)} files. (No write in Phase 0.4)")

    log_trace_event(
        "manifest_sync done",
        source=tool_name,
        tags=["tool", "done", "manifest_sync"],
        phase=REQUIRED_PHASE,
    )


if __name__ == "__main__":
    run_cli()

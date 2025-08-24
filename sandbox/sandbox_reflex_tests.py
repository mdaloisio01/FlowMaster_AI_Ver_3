# sandbox/sandbox_reflex_tests.py
# Runs only in sandbox/test mode. Loads seeds from top-level /seeds (never at normal startup).

from boot.boot_path_initializer import inject_paths
inject_paths()

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from core.phase_control import REQUIRED_PHASE, ensure_phase
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event

SEEDS_DIR = Path("seeds")


def _list_seed_files() -> List[Path]:
    if not SEEDS_DIR.exists():
        return []
    # Accept common text/markdown/json seeds
    exts = {".md", ".json", ".yaml", ".yml", ".txt", ".py"}
    return [p for p in sorted(SEEDS_DIR.rglob("*")) if p.is_file() and p.suffix in exts]


def run_cli() -> None:
    ensure_phase()
    tool_name = Path(__file__).as_posix()

    # Log that we're in sandbox and about to read seeds (no overwrites of real logs)
    log_memory_event(
        "sandbox_reflex_tests start (seed scan)",
        source=tool_name,
        tags=["sandbox", "start", "reflex_tests", "seed_scan"],
        content="starting",
        phase=REQUIRED_PHASE,
    )

    seeds = _list_seed_files()
    print(f"Seeds directory: {SEEDS_DIR.as_posix()}  |  files found: {len(seeds)}")
    for p in seeds[:20]:
        print(f" - {p.as_posix()}")

    # Example: read reflex manifest if present — but DO NOT write to logs/state
    manifest_path = SEEDS_DIR / "reflex_manifest.json"
    if manifest_path.exists():
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            print(f"reflex_manifest keys: {list(data)[:5]}")
        except Exception as e:
            print(f"Failed to read reflex_manifest.json: {e}")

    log_trace_event(
        "sandbox_reflex_tests done",
        source=tool_name,
        tags=["sandbox", "done", "reflex_tests", "seed_scan"],
        phase=REQUIRED_PHASE,
    )


if __name__ == "__main__":
    run_cli()

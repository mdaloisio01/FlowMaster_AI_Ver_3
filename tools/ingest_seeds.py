# tools/ingest_seeds.py
# One-time seed ingestion: reads files under /seeds and writes
# memory + trace events to prime Will, then drops a lock file so it won't repeat.
from __future__ import annotations

from boot.boot_path_initializer import inject_paths
inject_paths()

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import List, Dict, Any

from core.phase_control import REQUIRED_PHASE, ensure_phase
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event

SEEDS_DIR = Path("seeds")
LOCK_FILE = Path("root/first_boot.lock")

ALLOWED_EXTS = {".md", ".json", ".yaml", ".yml", ".txt", ".py"}


def _sha256_of_bytes(b: bytes) -> str:
    h = hashlib.sha256()
    h.update(b)
    return h.hexdigest()


def _list_seed_files() -> List[Path]:
    if not SEEDS_DIR.exists():
        return []
    return [p for p in sorted(SEEDS_DIR.rglob("*")) if p.is_file() and p.suffix in ALLOWED_EXTS]


def ingest_seeds(force: bool = False, dry_run: bool = False) -> Dict[str, Any]:
    """Ingest seeds once. Returns summary dict."""
    if LOCK_FILE.exists() and not force:
        return {"skipped": True, "reason": "lock_exists", "lock_path": LOCK_FILE.as_posix()}

    seeds = _list_seed_files()
    ingested = 0
    for p in seeds:
        meta: Dict[str, Any] = {"path": p.as_posix(), "size": p.stat().st_size}
        try:
            raw = p.read_bytes()
            meta["sha256"] = _sha256_of_bytes(raw)
            # Keep logs compact; do not stuff whole file contents.
        except Exception as e:
            meta["error"] = f"read_failed: {e}"

        if not dry_run:
            log_memory_event(
                event_text=f"seed ingested: {p.name}",
                source=Path(__file__).as_posix(),
                tags=["seed", "ingest"],
                content=meta,
                phase=REQUIRED_PHASE,
            )
        ingested += 1

    if not dry_run:
        LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
        LOCK_FILE.write_text(
            json.dumps(
                {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "reason": "seed_ingest"},
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    return {"skipped": False, "ingested": ingested, "lock_path": LOCK_FILE.as_posix()}


def run_cli() -> None:
    ensure_phase()
    tool = Path(__file__).as_posix()

    parser = argparse.ArgumentParser(description="One-time ingest of /seeds into memory/trace logs.")
    parser.add_argument("--force", action="store_true", help="Ignore lock and ingest again.")
    parser.add_argument("--dry-run", action="store_true", help="Scan and report, but do not write logs/lock.")
    args = parser.parse_args()

    log_memory_event(
        event_text=f"ingest_seeds start (force={args.force}, dry_run={args.dry_run})",
        source=tool,
        tags=["tool", "start", "seed_ingest"],
        content="starting",
        phase=REQUIRED_PHASE,
    )

    summary = ingest_seeds(force=args.force, dry_run=args.dry_run)
    if summary.get("skipped"):
        print(f"Seed ingest skipped (lock present): {summary.get('lock_path')}")
    else:
        print(f"Seed ingest complete: {summary.get('ingested', 0)} file(s).")
        print(f"Lock created at: {summary.get('lock_path')}")

    log_trace_event(
        description="ingest_seeds done",
        source=tool,
        tags=["tool", "done", "seed_ingest"],
        content=summary,
        phase=REQUIRED_PHASE,
    )


if __name__ == "__main__":
    run_cli()

from __future__ import annotations
from boot.boot_path_initializer import inject_paths
inject_paths()

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from core.phase_control import ensure_phase, REQUIRED_PHASE, get_current_phase
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event


PHASE_HISTORY = Path("configs/phase_history.json")
BUILD_LOG = Path("configs/build_log.json")


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_cli() -> None:
    ensure_phase()
    src = Path(__file__).as_posix()

    parser = argparse.ArgumentParser(description="Update phase_history/build_log entries.")
    parser.add_argument("--seal", action="store_true", help="Append a seal entry for the current phase.")
    parser.add_argument("--dry-run", action="store_true", help="Show changes but do not write files.")
    args = parser.parse_args()

    log_memory_event(
        event_text="update_phase_tracking start",
        source=src,
        tags=["tool", "start", "phase_tracking"],
        content={"seal": args.seal, "dry_run": args.dry_run, "current_phase": get_current_phase()},
        phase=REQUIRED_PHASE,
    )

    ph = _load_json(PHASE_HISTORY)
    bl = _load_json(BUILD_LOG)
    changed = {"phase_history": False, "build_log": False}

    if args.seal:
        # Add or update history
        entries = list(ph.get("history", []))
        entries.append({"phase": float(REQUIRED_PHASE), "ts": _now_iso()})
        ph["history"] = entries
        ph["current_phase"] = float(REQUIRED_PHASE)
        changed["phase_history"] = True

        # Append a build log stamp
        bl_entries = list(bl.get("builds", []))
        bl_entries.append({"phase": float(REQUIRED_PHASE), "ts": _now_iso(), "action": "sealed"})
        bl["builds"] = bl_entries
        changed["build_log"] = True

    if args.dry_run:
        print("DRY RUN: would write updates ->", changed)
    else:
        if changed["phase_history"]:
            PHASE_HISTORY.parent.mkdir(parents=True, exist_ok=True)
            PHASE_HISTORY.write_text(json.dumps(ph, ensure_ascii=False, indent=2), encoding="utf-8")
        if changed["build_log"]:
            BUILD_LOG.parent.mkdir(parents=True, exist_ok=True)
            BUILD_LOG.write_text(json.dumps(bl, ensure_ascii=False, indent=2), encoding="utf-8")

        if any(changed.values()):
            print("✅ phase_tracking updated:", {k: v for k, v in changed.items() if v})
        else:
            print("No changes. Pass --seal to append entries.")

    log_trace_event(
        description="update_phase_tracking done",
        source=src,
        tags=["tool", "done", "phase_tracking"],
        content={"changed": changed, "dry_run": args.dry_run},
        phase=REQUIRED_PHASE,
    )


if __name__ == "__main__":
    run_cli()

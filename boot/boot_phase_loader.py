# boot/boot_phase_loader.py
# Phase gate for boot + automatic one-time seed preload.
# Behavior:
#   - On first-ever boot (no lock file): ingest /seeds and create root/first_boot.lock
#   - On later boots: skip ingest and continue normally

from boot.boot_path_initializer import inject_paths
inject_paths()

from pathlib import Path
from typing import Dict, Any

from core.phase_control import REQUIRED_PHASE, get_current_phase, ensure_phase
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event

LOCK_FILE = Path("root/first_boot.lock")


def _ingest_seeds_once() -> Dict[str, Any]:
    """
    Ingest seeds exactly once per installation.
    Never raises; returns a summary dict.
    """
    if LOCK_FILE.exists():
        return {"skipped": True, "reason": "lock_exists", "lock_path": LOCK_FILE.as_posix()}

    # Import lazily to avoid overhead on normal boots
    try:
        from tools.ingest_seeds import ingest_seeds  # type: ignore
    except Exception as e:
        return {"skipped": True, "reason": f"import_failed: {e}"}

    try:
        summary = ingest_seeds(force=False, dry_run=False)
        return summary or {"skipped": False, "result": "ok"}
    except Exception as e:
        return {"skipped": True, "reason": f"ingest_failed: {e}"}


def run_cli() -> None:
    # Enforce phase before any boot actions
    ensure_phase()
    cur = get_current_phase()
    src = Path(__file__).as_posix()

    # Log boot start
    log_memory_event(
        event_text="boot_phase_loader start",
        source=src,
        tags=["boot", "start", "phase_loader"],
        content={"required_phase": REQUIRED_PHASE, "current_phase": cur},
        phase=REQUIRED_PHASE,
    )

    # Automatic one-time seed preload (first boot only)
    preload_summary = _ingest_seeds_once()
    if preload_summary.get("skipped"):
        reason = preload_summary.get("reason")
        if reason == "lock_exists":
            print(f"Seed preload: skipped (lock present at {preload_summary.get('lock_path')}).")
        else:
            # import_failed / ingest_failed etc.
            print(f"Seed preload: skipped ({reason}).")
    else:
        ing = preload_summary.get("ingested", 0)
        print(f"Seed preload: complete, ingested {ing} file(s).")
        if preload_summary.get("lock_path"):
            print(f"Lock created at: {preload_summary['lock_path']}")

    # Log boot done
    log_trace_event(
        description="boot_phase_loader done",
        source=src,
        tags=["boot", "done", "phase_loader"],
        content={"preload": preload_summary},
        phase=REQUIRED_PHASE,
    )

    print(f"Boot OK @ phase {cur} (required {REQUIRED_PHASE}).")


if __name__ == "__main__":
    run_cli()

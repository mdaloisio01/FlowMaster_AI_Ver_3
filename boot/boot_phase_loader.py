from __future__ import annotations
# boot/boot_phase_loader.py — boot loader (info-only phase, updated logging)

import sys
from pathlib import Path

# Ensure repo root on sys.path (.../boot -> repo root)
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from boot import boot_path_initializer as bpi
bpi.inject_paths()

from core.trace_logger import log_trace_event, log_memory_event
from core.phase_control import get_current_phase


def _lock_path() -> Path:
    # Matches the message you observed earlier: root/first_boot.lock
    return _REPO_ROOT / "root" / "first_boot.lock"


def run_cli() -> None:
    phase = get_current_phase()
    lp = _lock_path()

    # Start
    log_trace_event(
        "boot_phase_loader.start",
        {"lock": str(lp)},
        source="boot.boot_phase_loader",
        phase=phase,
    )

    try:
        if lp.exists():
            print("Seed preload: skipped (lock present at root/first_boot.lock).")
            log_trace_event(
                "boot_phase_loader.skip_seeding",
                {"lock": str(lp), "reason": "lock-present"},
                source="boot.boot_phase_loader",
                phase=phase,
            )
        else:
            # Prepare directories and create the lock to mark first-boot done.
            lp.parent.mkdir(parents=True, exist_ok=True)
            lp.write_text("ok", encoding="utf-8")

            log_memory_event(
                "boot_phase_loader.seeded",
                {"created_lock": str(lp)},
                source="boot.boot_phase_loader",
                phase=phase,
            )
            print("Seed preload: completed (lock created at root/first_boot.lock).")

        # Done
        log_trace_event(
            "boot_phase_loader.done",
            {"status": "ok"},
            source="boot.boot_phase_loader",
            phase=phase,
        )
    except Exception as e:
        # Log and re-raise as non-zero exit via SystemExit
        log_trace_event(
            "boot_phase_loader.error",
            {"error": repr(e)},
            source="boot.boot_phase_loader",
            phase=phase,
        )
        raise SystemExit(1)


if __name__ == "__main__":
    run_cli()

# tools/verify_log_integrity.py
from __future__ import annotations

from boot.boot_path_initializer import inject_paths
inject_paths()

import json
from pathlib import Path

from core.phase_control import REQUIRED_PHASE, ensure_phase
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event


MEM_FILE = Path("logs/will_memory_log.json")
TRACE_FILE = Path("logs/reflex_trace_log.json")
BOOT_FILE = Path("logs/boot_trace_log.json")


def _valid_json(path: Path) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8", errors="strict").strip()
    if not text:
        return True
    try:
        json.loads(text)
        return True
    except Exception:
        try:
            for line in text.splitlines():
                line = line.strip()
                if not line:
                    continue
                json.loads(line)
            return True
        except Exception:
            return False


def run_cli() -> None:
    ensure_phase()
    tool_name = Path(__file__).as_posix()

    log_memory_event(
        "verify_log_integrity start",
        source=tool_name,
        tags=["tool", "start", "verify_log_integrity"],
        content="starting",
        phase=REQUIRED_PHASE,
    )

    ok = all(_valid_json(p) for p in (MEM_FILE, TRACE_FILE, BOOT_FILE))
    print(f"Log integrity: {'OK' if ok else 'FAILED'}")

    log_trace_event(
        "verify_log_integrity done",
        source=tool_name,
        tags=["tool", "done", "verify_log_integrity"],
        phase=REQUIRED_PHASE,
    )

    if not ok:
        raise SystemExit(4)


if __name__ == "__main__":
    run_cli()

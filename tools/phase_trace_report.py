# tools/phase_trace_report.py
from __future__ import annotations

from boot.boot_path_initializer import inject_paths
inject_paths()

import json
from pathlib import Path
from typing import Any, List, Dict

from core.phase_control import REQUIRED_PHASE, ensure_phase
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event


MEM_FILE = Path("logs/will_memory_log.json")
TRACE_FILE = Path("logs/reflex_trace_log.json")


def _load_json_events(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return [data]
    except Exception:
        out: List[Dict[str, Any]] = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if isinstance(obj, dict):
                    out.append(obj)
            except Exception:
                continue
        return out
    return []


def run_cli() -> None:
    ensure_phase()

    tool_name = Path(__file__).as_posix()
    log_memory_event(
        "phase_trace_report start",
        source=tool_name,
        tags=["tool", "start", "phase_trace_report"],
        content="starting",
        phase=REQUIRED_PHASE,
    )

    mem = _load_json_events(MEM_FILE)
    trc = _load_json_events(TRACE_FILE)

    print(f"Phase Trace Report @ REQUIRED_PHASE={REQUIRED_PHASE}")
    print(f"- memory events: {len(mem)}")
    print(f"- trace events : {len(trc)}")

    log_trace_event(
        "phase_trace_report done",
        source=tool_name,
        tags=["tool", "done", "phase_trace_report"],
        phase=REQUIRED_PHASE,
    )


if __name__ == "__main__":
    run_cli()

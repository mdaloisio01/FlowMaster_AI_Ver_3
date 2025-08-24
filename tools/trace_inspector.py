# tools/trace_inspector.py
from __future__ import annotations

from boot.boot_path_initializer import inject_paths
inject_paths()

import argparse
import json
from pathlib import Path
from typing import List, Dict, Any

from core.phase_control import REQUIRED_PHASE, ensure_phase
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event


TRACE_FILE = Path("logs/reflex_trace_log.json")


def _load_events(path: Path) -> List[Dict[str, Any]]:
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
        events: List[Dict[str, Any]] = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if isinstance(obj, dict):
                    events.append(obj)
            except Exception:
                continue
        return events
    return []


def run_cli() -> None:
    ensure_phase()

    parser = argparse.ArgumentParser(description="Inspect trace log by tag.")
    parser.add_argument("--tag", type=str, default=None, help="Filter events containing this tag")
    parser.add_argument("--limit", type=int, default=50, help="Max events to show")
    args = parser.parse_args()

    tool_name = Path(__file__).as_posix()
    log_memory_event(
        f"trace_inspector start (tag={args.tag}, limit={args.limit})",
        source=tool_name,
        tags=["tool", "start", "trace_inspector"],
        content="starting",
        phase=REQUIRED_PHASE,
    )

    events = _load_events(TRACE_FILE)
    if args.tag:
        events = [e for e in events if isinstance(e, dict) and args.tag in (e.get("tags") or [])]

    out = events[-args.limit :] if args.limit and args.limit > 0 else events
    for e in out:
        desc = e.get("description") or e.get("event") or "event"
        tags = e.get("tags") or []
        print(f"- {desc}  tags={tags}")

    log_trace_event(
        "trace_inspector done",
        source=tool_name,
        tags=["tool", "done", "trace_inspector"],
        phase=REQUIRED_PHASE,
    )


if __name__ == "__main__":
    run_cli()

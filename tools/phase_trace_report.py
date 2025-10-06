#!/usr/bin/env python3
"""
Phase-neutral trace summary.
- Reads current phase from configs/ironroot_manifest_data.json
- Summarizes recent entries from logs/reflex_trace_log.jsonl (if present)
No dependency on boot/*.
"""

from __future__ import annotations
import json
from pathlib import Path
import sys
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = REPO_ROOT / "configs" / "ironroot_manifest_data.json"
TRACE_LOG = REPO_ROOT / "logs" / "reflex_trace_log.jsonl"

def read_manifest_phase() -> str:
    if not MANIFEST.exists():
        return "<manifest-missing>"
    try:
        with MANIFEST.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return str(data.get("current_phase", "") or "<phase-missing>").strip()
    except Exception as e:
        return f"<manifest-error:{e}>"

def tail_lines(path: Path, max_lines: int = 200) -> Iterable[str]:
    if not path.exists():
        return []
    try:
        # Simple, robust tail without external deps
        with path.open("r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()[-max_lines:]
        return lines
    except Exception:
        return []

def parse_trace(lines: Iterable[str], max_events: int = 50):
    events = []
    for raw in reversed(list(lines)):  # latest first
        raw = raw.strip()
        if not raw:
            continue
        try:
            obj = json.loads(raw)
            events.append({
                "ts": obj.get("ts") or obj.get("time") or "",
                "event": obj.get("event") or obj.get("type") or "",
                "source": obj.get("source") or obj.get("tool") or "",
                "status": obj.get("status") or "",
            })
            if len(events) >= max_events:
                break
        except Exception:
            # Skip non-JSON lines
            continue
    return events

def run_cli(argv: list[str]) -> int:
    phase = read_manifest_phase()
    print(f"current_phase: {phase}")

    if not TRACE_LOG.exists():
        print(f"trace: {TRACE_LOG} (absent)")
        return 0

    lines = tail_lines(TRACE_LOG, max_lines=500)
    events = parse_trace(lines, max_events=50)

    print(f"trace_file: {TRACE_LOG}")
    print(f"recent_events: {len(events)}")
    for e in events:
        ts = e["ts"] or "-"
        ev = e["event"] or "-"
        src = e["source"] or "-"
        st  = e["status"] or "-"
        print(f"- [{ts}] {ev} (src={src}, status={st})")
    return 0

if __name__ == "__main__":
    sys.exit(run_cli(sys.argv[1:]))

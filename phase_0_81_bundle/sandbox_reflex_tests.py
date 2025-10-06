#!/usr/bin/env python3
"""
Minimal heartbeat: writes one line to logs/reflex_trace_log.jsonl and logs/build_log.jsonl
Safe to run anywhere. Stdlib only.
"""
import json, datetime, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOGS = ROOT / "logs"
TRACE = LOGS / "reflex_trace_log.jsonl"
BUILD = LOGS / "build_log.jsonl"


def append_jsonl(path: pathlib.Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def main() -> int:
    ts = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    ping = {
        "ts": ts,
        "tool": "sandbox_reflex_tests",
        "action": "ping",
        "phase": "0.81",
        "msg": "Trace + build log heartbeat"
    }
    append_jsonl(TRACE, ping)
    append_jsonl(BUILD, {"ts": ts, "event": "phase_0_81_smoke_ok"})
    print("OK :: wrote heartbeat to ./logs/reflex_trace_log.jsonl and ./logs/build_log.jsonl")
    return 0


if __name__ == "__main__":
    sys.exit(main())

from __future__ import annotations
# core/trace_logger.py — central trace + memory logging (no phase enforcement)

import json
import time
from pathlib import Path
from typing import Any, Dict, Optional, Union

# Repo root (.../core -> repo root)
_REPO_ROOT = Path(__file__).resolve().parent.parent

# Log destinations (JSONL, append-only)
_LOG_DIR = _REPO_ROOT / "logs"
_LOG_DIR.mkdir(parents=True, exist_ok=True)
_TRACE_LOG = _LOG_DIR / "reflex_trace_log.jsonl"
_MEMORY_LOG = _LOG_DIR / "memory_log.jsonl"

Jsonable = Union[Dict[str, Any], str, int, float, None]


def _now_iso() -> str:
    # UTC ISO timestamp without subseconds for stable diffs
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _write_jsonl(path: Path, obj: Dict[str, Any]) -> None:
    try:
        with path.open("a", encoding="utf-8", newline="") as f:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
    except Exception:
        # Logging must never crash the app
        pass


def log_trace_event(
    event: str,
    data: Jsonable = None,
    *,
    source: Optional[str] = None,
    phase: Optional[float] = None,
    meta: Optional[Dict[str, Any]] = None,
    **extra: Any,
) -> None:
    """
    Record a trace event to logs/reflex_trace_log.jsonl.

    Back-compat: accepts optional keyword args like source=, phase=, meta=,
    and ignores any additional keywords via **extra.
    """
    entry: Dict[str, Any] = {
        "ts": _now_iso(),
        "event": str(event),
        "data": data,
        "source": source or "core.trace_logger",
    }
    if phase is not None:
        entry["phase"] = phase
    if meta:
        entry["meta"] = meta
    # If callers provided arbitrary extras, store them under "extra" to avoid loss.
    if extra:
        entry["extra"] = extra

    _write_jsonl(_TRACE_LOG, entry)


def log_memory_event(
    event_type: str,
    detail: Jsonable = None,
    meta: Optional[Dict[str, Any]] = None,
    *,
    source: Optional[str] = None,
    phase: Optional[float] = None,
    **extra: Any,
) -> None:
    """
    Record a memory event to logs/memory_log.jsonl.

    Back-compat: accepts optional source=, phase=, meta= and **extra.
    """
    entry: Dict[str, Any] = {
        "ts": _now_iso(),
        "type": str(event_type),
        "detail": detail,
        "meta": meta or {},
        "source": source or "core.trace_logger",
    }
    if phase is not None:
        entry["phase"] = phase
    if extra:
        entry["extra"] = extra

    _write_jsonl(_MEMORY_LOG, entry)


__all__ = ["log_trace_event", "log_memory_event"]

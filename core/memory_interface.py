# core/memory_interface.py
# Memory logging with UTF-8 writes and normalized, project-relative source paths.
# Writes a single JSON **array** at logs/will_memory_log.json.
# Compatible with both positional ("message", ...) and keyword-only (event_text=...) calling styles.

from __future__ import annotations

from boot.boot_path_initializer import inject_paths  # required path injection
inject_paths()

import json
import time
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List, Optional, Sequence

# Log destination (JSON array)
LOG_PATH = Path("logs/will_memory_log.json")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def _find_project_root() -> Path:
    """
    Heuristic: walk up until we find a marker directory typical for this repo,
    defaulting to current working dir if not found.
    """
    here = Path(".").resolve()
    for p in [here] + list(here.parents):
        if (p / "configs").exists() or (p / "core").exists():
            return p
    return here


def _now_iso() -> str:
    # UTC ISO-8601 Z format, no sub-second noise for stable diffs
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _rel_posix(path: Optional[str]) -> Optional[str]:
    if not path:
        return None
    try:
        root = _find_project_root()
        p = Path(path)
        if p.is_absolute():
            try:
                p = p.relative_to(root)
            except Exception:
                return PurePosixPath(p).as_posix()
        return PurePosixPath(p).as_posix()
    except Exception:
        return path.replace("\\", "/") if isinstance(path, str) else path


def _read_log_list() -> List[Dict[str, Any]]:
    try:
        with LOG_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        # If legacy newline-delimited file exists, salvage best-effort
        try:
            lines = [json.loads(line) for line in LOG_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
            return lines if isinstance(lines, list) else []
        except Exception:
            return []
    except Exception:
        return []


def _write_log_list(data: List[Dict[str, Any]]) -> None:
    # Pretty-print for human inspection; UTF-8; forward slashes in paths
    tmp = LOG_PATH.with_suffix(".tmp.json")
    with tmp.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    tmp.replace(LOG_PATH)


def log_memory_event(
    *args,
    event_text: Optional[str] = None,
    event_type: str = "info",
    source: Optional[str] = None,
    phase: Optional[float] = None,
    tags: Optional[Sequence[str]] = None,
    content: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Append a memory log entry.

    Call styles supported:
      - log_memory_event("some message", event_type="test_log", source="tools/trace_inspector.py", ...)
      - log_memory_event(event_text="some message", ...)

    Arguments:
        event_text: human message; mirrored to 'message' (tests assert 'message' exists).
        event_type: freeform type (e.g., 'test_log', 'test_error', ...)
        source: file path or logical source; normalized to forward slashes.
        phase: phase number for traceability (e.g., 0.2).
        tags: optional list of tags.
        content: optional structured payload.
        metadata: optional dict (accepted for test compatibility).

    Returns:
        The entry dict that was appended.
    """
    # Accept positional-first message for backward compatibility
    if event_text is None and len(args) >= 1:
        event_text = str(args[0])

    src = _rel_posix(source) if source else None

    entry: Dict[str, Any] = {
        "ts": _now_iso(),
        "message": str(event_text) if event_text is not None else "",  # tests check 'message'
        "event_text": str(event_text) if event_text is not None else "",
        "event_type": str(event_type),
        "source": src,
        "tags": list(tags or []),
        "content": content,
        "phase": phase,
    }
    if metadata is not None:
        entry["metadata"] = metadata

    data = _read_log_list()
    data.append(entry)
    _write_log_list(data)
    return entry


__all__ = ["log_memory_event"]

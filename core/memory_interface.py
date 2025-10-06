from __future__ import annotations
"""
core/memory_interface.py — Phase 0.7 (IronSpine)

- Append memory events to a single JSON *array* at logs/will_memory_log.json
- Back-compat call styles:
    log_memory_event("message", event_type="...", source="...")      # positional
    log_memory_event(event_text="message", ...)                      # keyword
- No imports from `boot` (prevents boot<->core circular imports)
"""

# === IronRoot Phase Guard (self-contained) ===
import os, sys, json, time
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List, Optional, Sequence

# Ensure repo root on path *without* importing boot
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from core.phase_control import ensure_phase  # safe (no boot import)
REQUIRED_PHASE: float = 0.7
ensure_phase(REQUIRED_PHASE)
# === /IronRoot Phase Guard ===


# Log destination: JSON array file (matches your current tests/tools)
LOG_PATH = _REPO_ROOT / "logs" / "will_memory_log.json"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def _now_iso() -> str:
    # UTC ISO-8601 Z format, no subseconds for stable diffs
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _find_project_root() -> Path:
    """
    Heuristic: walk up for common markers; fallback to current working dir.
    """
    here = _REPO_ROOT
    for p in [here] + list(here.parents):
        if (p / "configs").exists() or (p / "core").exists():
            return p
    return Path.cwd().resolve()


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
    except Exception:
        # On any parse error, fall back to empty (do not explode logging)
        return []


def _write_log_list(data: List[Dict[str, Any]]) -> None:
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
    Append a memory log entry to logs/will_memory_log.json (JSON array).

    Returns the appended entry.
    """
    # Accept positional-first message for backward compatibility
    if event_text is None and len(args) >= 1:
        event_text = str(args[0])

    entry: Dict[str, Any] = {
        "ts": _now_iso(),
        "message": str(event_text) if event_text is not None else "",
        "event_text": str(event_text) if event_text is not None else "",
        "event_type": str(event_type),
        "source": _rel_posix(source) if source else None,
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

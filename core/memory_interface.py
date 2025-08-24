# core/memory_interface.py
# Memory logging with UTF-8 writes and normalized, project-relative source paths.

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

LOG_PATH = Path("logs/will_memory_log.json")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def _find_project_root() -> Path:
    """
    Best-effort project root detection:
      - Walk up from this file until we find configs/ironroot_manifest_data.json
      - Else, first parent that contains "boot" and "core"
      - Else, current working directory
    """
    here = Path(__file__).resolve()
    for p in [here] + list(here.parents):
        try:
            if (p / "configs" / "ironroot_manifest_data.json").exists():
                return p
            if (p / "boot").is_dir() and (p / "core").is_dir():
                return p
        except Exception:
            continue
    return Path.cwd().resolve()


_PROJECT_ROOT = _find_project_root()
_PROJECT_ROOT_RESOLVED = _PROJECT_ROOT.resolve()


def _norm_slashes(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    return value.replace("\\", "/")


def _rel_source(value: Optional[str], default_file: str) -> str:
    """
    Normalize to forward slashes and make path project-relative when possible.
    If not a filesystem path or outside the project, return normalized absolute/as-is.
    """
    raw = _norm_slashes(value)
    try:
        if raw:
            p = Path(raw).resolve()
        else:
            p = Path(default_file).resolve()
    except Exception:
        # If resolution fails, just return normalized text
        return (raw or default_file).replace("\\", "/")

    try:
        rel = p.relative_to(_PROJECT_ROOT_RESOLVED)
        return rel.as_posix()
    except Exception:
        # Not under project root; return normalized absolute
        return p.as_posix()


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def log_memory_event(
    event_text: str,
    *,
    source: Optional[str] = None,
    tags: Optional[List[str]] = None,
    content: Optional[Union[str, Dict[str, Any], List[Any]]] = None,
    phase: Optional[Union[int, float, str]] = None,
    event_type: str = "event",
) -> None:
    """
    Append a memory event (NDJSON) to logs/will_memory_log.json.
    - Always UTF-8
    - `source` stored as project-relative path when possible (forward slashes)
    """
    src = _rel_source(source, default_file=__file__)

    rec: Dict[str, Any] = {
        "ts": _now_iso(),
        "event_text": str(event_text),
        "event_type": str(event_type),
        "source": src,
        "tags": list(tags or []),
        "content": content,
        "phase": phase,
    }

    line = json.dumps(rec, ensure_ascii=False)
    with LOG_PATH.open("a", encoding="utf-8", newline="\n") as f:
        f.write(line + "\n")

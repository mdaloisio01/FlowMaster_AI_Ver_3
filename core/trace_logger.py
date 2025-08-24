# core/trace_logger.py
# Trace logging with UTF-8 writes and normalized, project-relative source paths.

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

LOG_PATH = Path("logs/reflex_trace_log.json")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def _find_project_root() -> Path:
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
    raw = _norm_slashes(value)
    try:
        if raw:
            p = Path(raw).resolve()
        else:
            p = Path(default_file).resolve()
    except Exception:
        return (raw or default_file).replace("\\", "/")

    try:
        rel = p.relative_to(_PROJECT_ROOT_RESOLVED)
        return rel.as_posix()
    except Exception:
        return p.as_posix()


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def log_trace_event(
    description: str,
    *,
    source: Optional[str] = None,
    tags: Optional[List[str]] = None,
    content: Optional[Union[str, Dict[str, Any], List[Any]]] = None,
    phase: Optional[Union[int, float, str]] = None,
) -> None:
    """
    Append a trace event (NDJSON) to logs/reflex_trace_log.json.
    - Always UTF-8
    - `source` stored as project-relative path when possible (forward slashes)
    """
    src = _rel_source(source, default_file=__file__)

    rec: Dict[str, Any] = {
        "ts": _now_iso(),
        "description": str(description),
        "source": src,
        "tags": list(tags or []),
        "content": content,
        "phase": phase,
    }

    line = json.dumps(rec, ensure_ascii=False)
    with LOG_PATH.open("a", encoding="utf-8", newline="\n") as f:
        f.write(line + "\n")

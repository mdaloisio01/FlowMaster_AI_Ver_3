# boot/boot_trace_logger.py
# Boot trace logging with UTF-8 writes and project-relative paths.

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Optional

LOG_PATH = Path("logs/boot_trace_log.json")
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


def _rel_source(value: Optional[str], default_file: str) -> str:
    raw = (value or default_file).replace("\\", "/")
    try:
        p = Path(raw).resolve()
        return p.relative_to(_PROJECT_ROOT_RESOLVED).as_posix()
    except Exception:
        return Path(raw).as_posix()


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def log_boot_event(event: str, *, source: Optional[str] = None, content: Optional[Dict[str, Any]] = None) -> None:
    rec = {
        "ts": _now_iso(),
        "event": str(event),
        "source": _rel_source(source, __file__),
        "content": content or {},
    }
    with LOG_PATH.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

from __future__ import annotations
# core/phase_engine.py — phase info only (no enforcement)

import os, json
from pathlib import Path
from typing import Optional, Any

# Repo root (…/core -> repo root)
_REPO_ROOT = Path(__file__).resolve().parent.parent
_MANIFEST_PATH = _REPO_ROOT / "configs" / "ironroot_manifest_data.json"
_HISTORY_PATH  = _REPO_ROOT / "configs" / "phase_history.json"

# Default for display/telemetry only
DEFAULT_PHASE: float = 0.7

def _f(v: Any) -> Optional[float]:
    try:
        return float(v)
    except Exception:
        return None

def _env() -> Optional[float]:
    for k in ("WILL_CURRENT_PHASE", "FLOWMASTER_CURRENT_PHASE"):
        p = _f(os.environ.get(k))
        if p is not None:
            return p
    return None

def _manifest() -> Optional[float]:
    try:
        if not _MANIFEST_PATH.exists():
            return None
        data = json.loads(_MANIFEST_PATH.read_text(encoding="utf-8"))
        for k in ("current_phase", "phase"):
            p = _f(data.get(k))
            if p is not None:
                return p
    except Exception:
        pass
    return None

def _history() -> Optional[float]:
    try:
        if not _HISTORY_PATH.exists():
            return None
        data = json.loads(_HISTORY_PATH.read_text(encoding="utf-8"))
        for item in reversed(data.get("history", []) or []):
            p = _f(item.get("phase"))
            if p is not None:
                return p
    except Exception:
        pass
    return None

def get_current_phase() -> float:
    """Display/telemetry only; no enforcement."""
    return _env() or _manifest() or _history() or DEFAULT_PHASE

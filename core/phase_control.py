# core/phase_control.py

from boot.boot_path_initializer import inject_paths  # required path injection
inject_paths()

import os
import json
from pathlib import Path
from typing import Optional, Any

# Phase lock — update as you progress through phases
# After sealing 0.6 -> 0.7, REQUIRED_PHASE must be 0.7
REQUIRED_PHASE: float = 0.7


def _parse_phase(v: Any) -> Optional[float]:
    """Best-effort parse of phase values (accepts int/float/str)."""
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _read_phase_from_env() -> Optional[float]:
    """
    Highest priority: environment overrides.
    Recognized:
      - WILL_CURRENT_PHASE
      - FLOWMASTER_CURRENT_PHASE
    """
    for key in ("WILL_CURRENT_PHASE", "FLOWMASTER_CURRENT_PHASE"):
        val = os.environ.get(key)
        p = _parse_phase(val)
        if p is not None:
            return p
    return None


def _read_phase_from_manifest() -> Optional[float]:
    """
    Prefer the manifest's explicit current phase if present:
      configs/ironroot_manifest_data.json -> {"current_phase": 0.7, ...}
    Falls back to a top-level "phase" if that convention is used.
    """
    p = Path("configs/ironroot_manifest_data.json")
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None

    for key in ("current_phase", "phase"):
        ph = _parse_phase(data.get(key))
        if ph is not None:
            return ph
    return None


def _read_phase_from_history() -> Optional[float]:
    """
    Next priority: the tail of configs/phase_history.json["history"].
    We scan from the end to find the most recent numeric 'phase'.
    Entries may look like:
      {"phase": 0.6, "action": "sealed", "timestamp": "..."}
      {"phase": "0.7", "ts": "..."}
    """
    p = Path("configs/phase_history.json")
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        hist = data.get("history", []) or []
        # scan from newest to oldest for the first numeric phase
        for item in reversed(hist):
            ph = _parse_phase(item.get("phase"))
            if ph is not None:
                return ph
    except Exception:
        return None
    return None


def get_current_phase() -> float:
    """
    Current runtime phase.

    Order of precedence:
      1) Env var WILL_CURRENT_PHASE / FLOWMASTER_CURRENT_PHASE
      2) configs/ironroot_manifest_data.json -> current_phase (or phase)
      3) configs/phase_history.json -> last numeric 'phase'
      4) REQUIRED_PHASE (fallback)
    """
    return (
        _read_phase_from_env()
        or _read_phase_from_manifest()
        or _read_phase_from_history()
        or REQUIRED_PHASE
    )


def ensure_phase(required: Optional[float] = None) -> None:
    """
    Enforce phase lock. Call this at the start of every CLI tool/reflex.
    Raises RuntimeError if current != required.
    """
    req = REQUIRED_PHASE if required is None else float(required)
    cur = float(get_current_phase())
    if cur != req:
        raise RuntimeError(
            f"IRONROOT VIOLATION: Phase mismatch. required={req} current={cur}. "
            "All tools/reflexes must obey REQUIRED_PHASE from core.phase_control."
        )


__all__ = ["REQUIRED_PHASE", "get_current_phase", "ensure_phase"]

# core/phase_control.py
# Single source of truth for phase gating.
# All tools/reflexes/tests must import REQUIRED_PHASE and get_current_phase from here.
# Paths use forward slashes; all JSON I/O uses UTF-8.

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Optional

# ---- Phase constant (authoritative) ----
# Phase 0.4 – Trace Validation & Reflex Compliance
REQUIRED_PHASE: float = 0.4

# Optional: file that may record the latest sealed phase.
_PHASE_HISTORY_FILE = Path("configs/phase_history.json")


def _read_phase_from_env() -> Optional[float]:
    """Allow overriding the runtime phase via env var (e.g., in CI)."""
    val = os.getenv("WILL_CURRENT_PHASE") or os.getenv("FLOWMASTER_CURRENT_PHASE")
    if not val:
        return None
    try:
        return float(val)
    except Exception:
        return None


def _read_phase_from_file() -> Optional[float]:
    """
    Try several reasonable shapes for configs/phase_history.json:
      1) {"current_phase": 0.4}
      2) {"history": [{"phase": 0.1, ...}, {"phase": 0.4, ...}]}
      3) [{"phase": 0.1, ...}, {"phase": 0.4, ...}]
    On any error, return None (caller will fall back to REQUIRED_PHASE).
    """
    try:
        if not _PHASE_HISTORY_FILE.exists():
            return None
        data: Any = json.loads(_PHASE_HISTORY_FILE.read_text(encoding="utf-8"))

        # shape 1
        if isinstance(data, dict) and "current_phase" in data:
            return float(data["current_phase"])

        # shape 2
        if isinstance(data, dict) and "history" in data and isinstance(data["history"], list):
            hist = data["history"]
            if hist:
                last = hist[-1]
                if isinstance(last, dict) and "phase" in last:
                    return float(last["phase"])

        # shape 3
        if isinstance(data, list) and data:
            last = data[-1]
            if isinstance(last, dict) and "phase" in last:
                return float(last["phase"])
    except Exception:
        return None
    return None


def get_current_phase() -> float:
    """
    Current runtime phase.
    Order of precedence:
      1) Env var WILL_CURRENT_PHASE / FLOWMASTER_CURRENT_PHASE
      2) configs/phase_history.json
      3) REQUIRED_PHASE (fallback)
    """
    return _read_phase_from_env() or _read_phase_from_file() or REQUIRED_PHASE


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


__all__ = ("REQUIRED_PHASE", "get_current_phase", "ensure_phase")

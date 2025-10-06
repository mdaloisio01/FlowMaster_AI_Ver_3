#!/usr/bin/env python3
"""
Phase control helpers for Will (IronRoot Law compatible).
- REQUIRED_PHASE is metadata for tools; default enforcement is SOFT (no hard fail at import).
- Call ensure_phase(REQUIRED_PHASE) explicitly in tools/reflexes that want strict checks.

Safe in git hooks and general imports.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional, Tuple

# --- CONFIG -----------------------------------------------------------------
# The phase your current branch/work should target. Bump this when advancing.
REQUIRED_PHASE: float = 0.81

# Soft mode: if True, ensure_phase() logs a warning instead of raising.
# Set to False only if you explicitly want hard enforcement in a given tool.
SOFT_MODE: bool = True

# Default paths
REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "configs" / "ironroot_manifest_data.json"
SEALS_DIR = REPO_ROOT / "seals"

# --- UTILS ------------------------------------------------------------------

def _read_manifest_phase(path: Path = MANIFEST_PATH) -> Optional[float]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        p = data.get("current_phase")
        # allow strings like "0.81"
        return float(p) if p is not None else None
    except Exception:
        return None


def get_current_phase() -> Optional[float]:
    """Return the manifest's current_phase as float, or None if unavailable."""
    return _read_manifest_phase(MANIFEST_PATH)


def _cmp(a: float, b: float, tol: float = 1e-9) -> int:
    d = a - b
    if abs(d) <= tol:
        return 0
    return -1 if d < 0 else 1


def _format_violation(required: float, current: Optional[float]) -> str:
    return (
        "IRONROOT VIOLATION: Phase mismatch. "
        f"required={required} current={current}. "
        "Set REQUIRED_PHASE in core.phase_control or update configs/ironroot_manifest_data.json."
    )


# --- ENFORCEMENT ------------------------------------------------------------

def ensure_phase(required: Optional[float] = None, *, soft: Optional[bool] = None) -> bool:
    """
    Ensure the manifest's current_phase matches the required phase (==).
    - If soft (default True or SOFT_MODE), logs to stderr and returns False on mismatch.
    - If hard (soft=False), raises RuntimeError on mismatch.
    Returns True when phases match exactly.
    """
    req = REQUIRED_PHASE if required is None else float(required)
    cur = get_current_phase()

    if cur is None:
        msg = "[phase] manifest missing or unreadable; skipping strict check"
        if (SOFT_MODE if soft is None else soft):
            sys.stderr.write(msg + "\n")
            return False
        raise RuntimeError(msg)

    ok = _cmp(cur, req) == 0
    if ok:
        return True

    # Mismatch
    message = _format_violation(req, cur)
    if (SOFT_MODE if soft is None else soft):
        sys.stderr.write("[phase-soft] " + message + "\n")
        return False
    raise RuntimeError(message)


def ensure_sealed_through(target: float) -> bool:
    """Return True if ./seals contains phase_0_X.sealed files up to floor(target*10)/10."""
    try:
        upto = int(float(target) * 10)
        for i in range(1, upto + 1):
            name = f"phase_0_{i}.sealed"
            if not (SEALS_DIR / name).exists():
                return False
        return True
    except Exception:
        return False


__all__ = [
    "REQUIRED_PHASE",
    "SOFT_MODE",
    "get_current_phase",
    "ensure_phase",
    "ensure_sealed_through",
]

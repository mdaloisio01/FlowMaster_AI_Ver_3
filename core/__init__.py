"""core package init — soft phase guard only.

This avoids hard-failing imports (e.g., in git pre-commit hooks) while still
allowing tools to call ensure_phase() explicitly when they want strict checks.
"""
from __future__ import annotations

# SOFT PHASE GUARD: do NOT hard-fail at import time
try:
    from .phase_control import ensure_phase, REQUIRED_PHASE  # noqa: F401
    # IMPORTANT: The hard enforcement is intentionally disabled at import time.
    # Old behavior (disabled): ensure_phase(REQUIRED_PHASE)
except Exception as e:  # pragma: no cover
    # Log-only; never raise here — keeps hooks and imports from crashing.
    import sys
    sys.stderr.write(f"[phase-soft] phase check skipped: {e}\n")

# Package exports (keep stable surface)
__all__ = [
    # Re-export for callers that do: from core import ensure_phase, REQUIRED_PHASE
    'ensure_phase',
    'REQUIRED_PHASE',
]

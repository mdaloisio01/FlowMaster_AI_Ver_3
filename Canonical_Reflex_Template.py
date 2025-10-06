from __future__ import annotations
# Canonical_Reflex_Template.py - Phase 0.7 guard

# === IronRoot Phase Guard (auto-injected) ===
import os, sys
REQUIRED_PHASE = 0.7
if os.path.abspath(os.path.join(os.path.dirname(__file__), "")) not in sys.path:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "")))
from core.phase_control import ensure_phase
ensure_phase(REQUIRED_PHASE)
# === /IronRoot Phase Guard ===

# Minimal safe template exports
def run_cli() -> int:
    return 0

if __name__ == "__main__":
    raise SystemExit(run_cli())

from __future__ import annotations

# === IronRoot Phase Guard (auto-injected) ===
# Minimal path setup here (do NOT import from boot to avoid circular imports).
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.phase_control import ensure_phase
REQUIRED_PHASE = 0.7
ensure_phase(REQUIRED_PHASE)
# === /IronRoot Phase Guard ===

# /FlowMaster_AI_Ver_3/core/__init__.py
# Core system module for Will
# Houses memory engine, manifest DB, SQLite bootstrap, and interface wrappers

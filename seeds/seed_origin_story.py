# === IronRoot Phase Guard (auto-injected) ===
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from boot.boot_path_initializer import inject_paths
inject_paths()
from core.phase_control import ensure_phase
REQUIRED_PHASE = 0.7
ensure_phase(REQUIRED_PHASE)
# === /IronRoot Phase Guard ===

# seeds/seed_origin_story.py

def seed_origin_story():
    return {
        "system": "origin_story",
        "description": "Foundational context about how this Will instance was created and what it is evolving toward.",
        "version": "1.0",
        "tags": ["core", "origin", "context"],
        "values": {
            "founder": "Mark",
            "purpose": "To assist, automate, and evolve alongside its operator.",
            "milestones": [
                "Phase 1: Reflex engine live",
                "Phase 2: Memory + seed boot complete",
                "Phase 3: GUI + Natural Language Runtime",
                "Phase 4: Modular Autonomy & Deployment"
            ]
        }
    }
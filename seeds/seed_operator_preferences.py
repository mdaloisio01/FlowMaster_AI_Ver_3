# === IronRoot Phase Guard (auto-injected) ===
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from boot.boot_path_initializer import inject_paths
inject_paths()
from core.phase_control import ensure_phase
REQUIRED_PHASE = 0.7
ensure_phase(REQUIRED_PHASE)
# === /IronRoot Phase Guard ===

# seeds/seed_operator_preferences.py

def seed_operator_preferences():
    return {
        "system": "operator_preferences",
        "description": "Defines preferences, toggles, and environment settings for the operator of this Will instance.",
        "version": "1.0",
        "tags": ["core", "operator", "settings"],
        "values": {
            "preferred_language": "en",
            "debug_mode": True,
            "auto_backup": True,
            "reflex_autoload": True,
            "default_prompt_mode": "structured"
        }
    }
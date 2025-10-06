# === IronRoot Phase Guard (auto-injected) ===
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from boot.boot_path_initializer import inject_paths
inject_paths()
from core.phase_control import ensure_phase
REQUIRED_PHASE = 0.7
ensure_phase(REQUIRED_PHASE)
# === /IronRoot Phase Guard ===

# seeds/seed_ironroot_summary.py

def seed_ironroot_summary():
    return {
        "system": "ironroot_summary",
        "description": "Top-level summary of the Ironroot AI architecture and design philosophy.",
        "version": "1.0",
        "tags": ["core", "ironroot", "summary"],
        "values": {
            "mission": "To quietly power the backbone of small businesses using smart, adaptive, autonomous systems.",
            "core_principles": [
                "Reliability over flash",
                "Simplicity over complexity",
                "System over ego"
            ],
            "modules": [
                "Reflex engine",
                "Memory stack",
                "Seed bootloader",
                "Toolchain loader"
            ]
        }
    }
# === IronRoot Phase Guard (auto-injected) ===
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from boot.boot_path_initializer import inject_paths
inject_paths()
from core.phase_control import ensure_phase
REQUIRED_PHASE = 0.7
ensure_phase(REQUIRED_PHASE)
# === /IronRoot Phase Guard ===

# /FlowMaster_AI_Ver_3/sandbox/__init__.py

from core.memory_interface import log_memory_event

def run_cli():
    print("🧪 Sandbox module loaded.")
    log_memory_event(
        event_text="Sandbox module __init__ loaded",
        event_type="sandbox_boot",
        source="sandbox.__init__",
        phase=0.2,
        metadata={"status": "ok"}
    )

if __name__ == "__main__":
    run_cli()

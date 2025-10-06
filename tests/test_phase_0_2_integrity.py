# === IronRoot Phase Guard (auto-injected) ===
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from boot.boot_path_initializer import inject_paths
inject_paths()
from core.phase_control import ensure_phase
REQUIRED_PHASE = 0.7
ensure_phase(REQUIRED_PHASE)
# === /IronRoot Phase Guard ===

# /FlowMaster_AI_Ver_3/tests/test_phase_0_2_integrity.py

from boot.boot_path_initializer import inject_paths
inject_paths()

from core.manifest_db import fetch_all_manifest
from core.memory_log_db import fetch_all_memory_logs
from core.reflex_registry_db import fetch_all_reflexes
from core.sqlite_bootstrap import insert_boot_report_entry
from core.memory_interface import log_memory_event

def run_test():
    print("🧪 Running Phase 0.2 Integrity Check...")

    try:
        # Confirm DB tables return expected structure
        manifest = fetch_all_manifest()
        reflexes = fetch_all_reflexes()
        memory_logs = fetch_all_memory_logs()

        assert isinstance(manifest, list)
        assert isinstance(reflexes, list)
        assert isinstance(memory_logs, list)

        assert all("file_path" in row for row in manifest)
        assert all("reflex_name" in row for row in reflexes)
        assert all("message" in row for row in memory_logs)

        insert_boot_report_entry("✅ Phase 0.2 Integrity Check Passed")

        log_memory_event(
            event_text="🧪 Phase 0.2 Integrity Check Passed",
            event_type="test_log",
            source="test_phase_0_2_integrity.py",
            phase=0.2,
            metadata={"status": "ok"}
        )

        print("✅ Phase 0.2 Integrity Test PASSED")

    except Exception as e:
        log_memory_event(
            event_text=f"❌ Phase 0.2 Integrity Test FAILED: {str(e)}",
            event_type="test_error",
            source="test_phase_0_2_integrity.py",
            phase=0.2,
            metadata={"error": str(e)}
        )
        print("❌ Phase 0.2 Integrity Test FAILED")
        raise

if __name__ == "__main__":
    run_test()

# tests/test_phase_0_6_preseal_end_to_end.py
from boot.boot_path_initializer import inject_paths
inject_paths()

import subprocess, sys
from core.phase_control import REQUIRED_PHASE, ensure_phase

def _run(mod, *args):
    return subprocess.run([sys.executable, "-m", mod, *args], capture_output=True, text=True)

def test_golden_preflight_core_sequence():
    ensure_phase(REQUIRED_PHASE)

    assert _run("core.sqlite_bootstrap").returncode == 0
    assert _run("tools.check_db_tables").returncode == 0
    assert _run("tools.manifest_history_auditor").returncode == 0

    # Compliance guard may allow "skipped_future", but must not crash
    cg = _run("tools.reflex_compliance_guard")
    assert cg.returncode == 0

    # Snapshot and cross-check
    assert _run("tools.trace_memory_snapshot", "--snapshot-mode", "light").returncode == 0
    x = _run("tools.trace_memory_crosscheck")
    assert x.returncode == 0

    # Schema audit passes (after migration)
    a1 = _run("tools.db_schema_migrate", "--apply", "--reason", "preseal_end_to_end")
    assert a1.returncode == 0
    a2 = _run("tools.db_schema_contract", "--assert")
    assert a2.returncode == 0

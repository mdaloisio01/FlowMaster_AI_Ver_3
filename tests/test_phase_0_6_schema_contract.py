# tests/test_phase_0_6_schema_contract.py
from boot.boot_path_initializer import inject_paths
inject_paths()

import subprocess, sys
from core.phase_control import REQUIRED_PHASE, ensure_phase

def test_schema_contract_green_after_migrate():
    ensure_phase(REQUIRED_PHASE)
    res1 = subprocess.run([sys.executable, "-m", "tools.db_schema_migrate", "--apply", "--reason", "phase_0_6_contract"], capture_output=True, text=True)
    assert res1.returncode == 0, res1.stderr

    res2 = subprocess.run([sys.executable, "-m", "tools.db_schema_contract", "--assert"], capture_output=True, text=True)
    assert res2.returncode == 0, res2.stderr

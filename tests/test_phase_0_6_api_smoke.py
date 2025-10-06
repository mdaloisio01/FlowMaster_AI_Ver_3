# tests/test_phase_0_6_api_smoke.py
from boot.boot_path_initializer import inject_paths
inject_paths()

import importlib
import subprocess, sys
from core.phase_control import REQUIRED_PHASE, ensure_phase

def _run_module(mod, *args):
    cmd = [sys.executable, "-m", mod, *args]
    return subprocess.run(cmd, capture_output=True, text=True)

def test_phase_lock():
    ensure_phase(REQUIRED_PHASE)

def test_core_surfaces_present_and_callable():
    # core.manifest_db
    mdb = importlib.import_module("core.manifest_db")
    assert hasattr(mdb, "fetch_all_manifest")
    assert hasattr(mdb, "upsert_manifest_path")
    # core.reflex_registry_db
    rdb = importlib.import_module("core.reflex_registry_db")
    assert hasattr(rdb, "fetch_all_reflexes")
    assert hasattr(rdb, "register_reflex")
    # core.sqlite_bootstrap
    sdb = importlib.import_module("core.sqlite_bootstrap")
    assert hasattr(sdb, "DB_PATH")
    assert any(hasattr(sdb, name) for name in ("ensure_bootstrap","ensure_tables","bootstrap"))

def test_tools_runnable_minimum():
    # trace_inspector (help must be runnable)
    res = _run_module("tools.trace_inspector", "--help")
    assert res.returncode == 0
    # db_snapshot_auditor (must import/run)
    res2 = _run_module("tools.db_snapshot_auditor")
    assert res2.returncode == 0

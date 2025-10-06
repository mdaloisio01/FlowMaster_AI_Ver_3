# tools/run_all_phase_tests.py
from boot.boot_path_initializer import inject_paths
inject_paths()

import sys, subprocess, glob
from pathlib import Path
from core.phase_control import REQUIRED_PHASE, ensure_phase
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event

def _to_module(path_str: str) -> str:
    """
    Convert a filesystem path like 'tests/test_phase_0_6_roundtrip.py'
    into a module name 'tests.test_phase_0_6_roundtrip' WITHOUT mangling names.
    """
    p = Path(path_str).as_posix()
    if p.endswith(".py"):
        p = p[:-3]  # remove the exact .py suffix
    return p.replace("/", ".")

def main():
    ensure_phase(REQUIRED_PHASE)
    run_id = "run_all_phase_tests"
    log_memory_event("run_all_phase_tests:start", source=__file__, tags=["tool","start"], phase=REQUIRED_PHASE, content={"run_id":run_id})
    log_trace_event("run_all_phase_tests:start", source=__file__, tags=["tool","start"], phase=REQUIRED_PHASE, content={"run_id":run_id})

    test_files = sorted(glob.glob("tests/test_phase_*.py"))
    tests = [_to_module(p) for p in test_files]

    overall_ok = True
    for mod_path in tests:
        print(f"[run] {mod_path}")
        res = subprocess.run([sys.executable, "-m", mod_path], text=True)
        if res.returncode != 0:
            overall_ok = False
            print(f"[fail] {mod_path} -> {res.returncode}")

    log_memory_event("run_all_phase_tests:report", source=__file__, tags=["tool","report"], phase=REQUIRED_PHASE, content={"run_id":run_id,"count":len(tests),"ok":overall_ok})
    log_trace_event("run_all_phase_tests:done", source=__file__, tags=["tool","done"], phase=REQUIRED_PHASE, content={"run_id":run_id})

    sys.exit(0 if overall_ok else 1)

if __name__ == "__main__":
    main()

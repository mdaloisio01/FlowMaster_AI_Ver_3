# tools/api_smoke_suite.py
from boot.boot_path_initializer import inject_paths
inject_paths()

import argparse, importlib, sys, subprocess
from typing import List, Tuple
from core.phase_control import REQUIRED_PHASE, ensure_phase
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event

def _ok(name:str, msg:str)->str: return f"✔ {name} — {msg}"
def _bad(name:str, msg:str)->str: return f"✖ {name} — {msg}"

def main():
    ensure_phase(REQUIRED_PHASE)
    ap = argparse.ArgumentParser()
    ap.parse_args()

    run_id = "api_smoke_suite"
    log_memory_event("api_smoke:start", source=__file__, tags=["tool","start"], phase=REQUIRED_PHASE, content={"run_id":run_id})
    log_trace_event("api_smoke:start", source=__file__, tags=["tool","start"], phase=REQUIRED_PHASE, content={"run_id":run_id})

    results: List[str] = []
    exit_code = 0

    # core.manifest_db
    try:
        mdb = importlib.import_module("core.manifest_db")
        assert hasattr(mdb, "fetch_all_manifest") and hasattr(mdb, "upsert_manifest_path")
        results.append(_ok("core.manifest_db", "API present"))
    except Exception as e:
        results.append(_bad("core.manifest_db", f"{e}"))
        exit_code = 1

    # core.reflex_registry_db
    try:
        rdb = importlib.import_module("core.reflex_registry_db")
        assert hasattr(rdb, "fetch_all_reflexes") and hasattr(rdb, "register_reflex")
        results.append(_ok("core.reflex_registry_db", "API present"))
    except Exception as e:
        results.append(_bad("core.reflex_registry_db", f"{e}"))
        exit_code = 1

    # core.sqlite_bootstrap
    try:
        sdb = importlib.import_module("core.sqlite_bootstrap")
        ok = hasattr(sdb, "DB_PATH") and any(hasattr(sdb, n) for n in ("ensure_bootstrap","ensure_tables","bootstrap"))
        if ok:
            results.append(_ok("core.sqlite_bootstrap", "DB_PATH + ensure_* present"))
        else:
            raise RuntimeError("missing ensure_* or DB_PATH")
    except Exception as e:
        results.append(_bad("core.sqlite_bootstrap", f"{e}"))
        exit_code = 1

    # core.memory_interface + core.trace_logger
    try:
        import core.memory_interface as mi
        import core.trace_logger as tl
        assert hasattr(mi, "log_memory_event") and hasattr(tl, "log_trace_event")
        results.append(_ok("memory/trace logging", "both present"))
    except Exception as e:
        results.append(_bad("memory/trace logging", f"{e}"))
        exit_code = 1

    # tools.trace_inspector
    try:
        res = subprocess.run([sys.executable, "-m", "tools.trace_inspector", "--help"], capture_output=True, text=True)
        if res.returncode == 0:
            results.append(_ok("tools.trace_inspector", "runnable"))
        else:
            raise RuntimeError(res.stderr.strip() or "trace_inspector non-zero")
    except Exception as e:
        results.append(_bad("tools.trace_inspector", f"{e}"))
        exit_code = 1

    # tools.db_snapshot_auditor
    try:
        res = subprocess.run([sys.executable, "-m", "tools.db_snapshot_auditor"], capture_output=True, text=True)
        if res.returncode == 0:
            results.append(_ok("tools.db_snapshot_auditor", "runnable"))
        else:
            raise RuntimeError(res.stderr.strip() or "db_snapshot_auditor non-zero")
    except Exception as e:
        results.append(_bad("tools.db_snapshot_auditor", f"{e}"))
        exit_code = 1

    for line in results:
        print(line)

    log_memory_event("api_smoke:report", source=__file__, tags=["tool","report"], phase=REQUIRED_PHASE, content={"run_id":run_id,"results":results})
    log_trace_event("api_smoke:done", source=__file__, tags=["tool","done"], phase=REQUIRED_PHASE, content={"run_id":run_id})
    sys.exit(exit_code)

if __name__ == "__main__":
    main()

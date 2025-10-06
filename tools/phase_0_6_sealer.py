# tools/phase_0_6_sealer.py
from boot.boot_path_initializer import inject_paths
inject_paths()

import argparse, json, subprocess, sys, os
from pathlib import Path
from core.phase_control import REQUIRED_PHASE, ensure_phase, get_current_phase
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event

def _run_ok(mod: str, *args) -> None:
    res = subprocess.run([sys.executable, "-m", mod, *args], capture_output=True, text=True)
    if res.returncode != 0:
        sys.stderr.write(res.stderr or res.stdout)
        raise SystemExit(1)

def _golden_preflight() -> None:
    _run_ok("core.sqlite_bootstrap")
    _run_ok("tools.check_db_tables")
    _run_ok("tools.manifest_history_auditor")
    _run_ok("tools.reflex_compliance_guard")
    _run_ok("tools.trace_memory_snapshot", "--snapshot-mode", "light")
    _run_ok("tools.trace_memory_crosscheck")
    _run_ok("tools.db_schema_migrate", "--apply", "--reason", "phase_0_6_seal")
    _run_ok("tools.db_schema_contract", "--assert")
    _run_ok("tools.run_all_phase_tests")

def _bump_manifest_to_0_7(dry_run: bool) -> None:
    p = Path("configs/ironroot_manifest_data.json")
    if not p.exists():
        raise SystemExit("manifest missing at configs/ironroot_manifest_data.json")
    data = json.loads(p.read_text(encoding="utf-8"))
    data["current_phase"] = 0.7
    if dry_run:
        print("[dry-run] would set current_phase -> 0.7")
    else:
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

def main():
    ensure_phase(REQUIRED_PHASE)  # must be 0.6 prior to bump
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    run_id = "phase_0_6_sealer"
    log_memory_event("phase_0_6_sealer:start", source=__file__, tags=["tool","start"], phase=REQUIRED_PHASE, content={"run_id":run_id,"dry_run":args.dry_run})
    log_trace_event("phase_0_6_sealer:start", source=__file__, tags=["tool","start"], phase=REQUIRED_PHASE, content={"run_id":run_id,"dry_run":args.dry_run})

    _golden_preflight()
    _bump_manifest_to_0_7(dry_run=args.dry_run)

    if not args.dry_run:
        # Verify post-bump
        cur = get_current_phase()
        print(f"Post-bump current phase: {cur}")

    log_memory_event("phase_0_6_sealer:done", source=__file__, tags=["tool","done"], phase=REQUIRED_PHASE, content={"run_id":run_id})
    log_trace_event("phase_0_6_sealer:done", source=__file__, tags=["tool","done"], phase=REQUIRED_PHASE, content={"run_id":run_id})

if __name__ == "__main__":
    main()

# tools/manifest_history_auditor.py
# Verifies manifest/history/dev_file_list contain required Phase 0.5 entries.
# Optional --auto-fix uses ironroot_registrar to add any missing entries.
# IronRoot: path injection first, phase lock, dual logging, UTF-8, forward slashes.

from boot.boot_path_initializer import inject_paths
inject_paths()

import argparse
import json
from pathlib import Path
from typing import List

from core.phase_control import ensure_phase, REQUIRED_PHASE
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event

MANIFEST = Path("configs/ironroot_manifest_data.json")
HISTORY = Path("configs/ironroot_file_history_with_dependencies.json")
DEVLIST = Path("configs/dev_file_list.md")

PHASE_FILES = [
    "core/snapshot_manager.py",
    "reflexes/reflex_core/reflex_table_tick.py",
    "reflexes/reflex_core/reflex_trace_ping.py",
    "tests/test_phase_0_5_snapshot_diffs.py",
    "tests/test_phase_0_5_trace_memory_integrity.py",
    "tools/db_snapshot_auditor.py",
    "tools/trace_memory_crosscheck.py",
    "tools/trace_memory_snapshot.py",
    "tools/phase_0_5_sealer.py",
]

def _read_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))

def _in_manifest(mani: dict, f: str) -> bool:
    in_files = f in mani.get("files", [])
    in_all = f in mani.get("manifest", {}).get("all_files", [])
    cat = f.split("/", 1)[0] if "/" in f else "root"
    in_cat = f in mani.get("manifest", {}).get(cat, [])
    return in_files and in_all and in_cat

def _in_history(hist: dict, f: str) -> bool:
    # Auditor expects dict form: {"history": { "<path>": {...} } }
    return f in hist.get("history", {})

def _in_devlist(text: str, f: str) -> bool:
    return any(line.strip() == f for line in text.splitlines())

def run_cli() -> None:
    ensure_phase()

    ap = argparse.ArgumentParser(description="Manifest/History Auditor", allow_abbrev=False)
    ap.add_argument("--auto-fix", action="store_true", help="If set, missing entries are added via ironroot_registrar --apply.")
    args = ap.parse_args()

    payload_start = {"auto_fix": bool(args.auto_fix), "phase_files": PHASE_FILES}
    src = __file__.replace("\\", "/")
    log_memory_event("manifest_history_auditor start", source=src, tags=["tool", "manifest", "history", "start"], content=payload_start, phase=REQUIRED_PHASE)
    log_trace_event("manifest_history_auditor start", source=src, tags=["tool", "manifest", "history", "start"], content=payload_start, phase=REQUIRED_PHASE)

    mani = _read_json(MANIFEST)
    hist = _read_json(HISTORY)
    dev_text = DEVLIST.read_text(encoding="utf-8") if DEVLIST.exists() else ""

    missing_manifest: List[str] = []
    missing_history: List[str] = []
    missing_devlist: List[str] = []

    for f in PHASE_FILES:
        if not _in_manifest(mani, f):
            missing_manifest.append(f)
        if not _in_history(hist, f):
            missing_history.append(f)
        if not _in_devlist(dev_text, f):
            missing_devlist.append(f)

    # Human stdout
    print("[audit] manifest missing:", missing_manifest or "none")
    print("[audit] history missing:", missing_history or "none")
    print("[audit] dev_file_list missing:", missing_devlist or "none")

    # NEW: explicit report triplet event
    payload_report = {
        "missing_manifest": missing_manifest,
        "missing_history": missing_history,
        "missing_devlist": missing_devlist,
        "auto_fix_requested": bool(args.auto_fix),
    }
    log_memory_event("manifest_history_auditor report", source=src, tags=["tool", "manifest", "history", "report"], content=payload_report, phase=REQUIRED_PHASE)
    log_trace_event("manifest_history_auditor report", source=src, tags=["tool", "manifest", "history", "report"], content=payload_report, phase=REQUIRED_PHASE)

    if args.auto_fix and (missing_manifest or missing_history or missing_devlist):
        # Register the union of missing files
        todo = sorted({*missing_manifest, *missing_history, *missing_devlist})
        import subprocess, sys, json as _json
        cmd = [
            sys.executable, "-m", "tools.ironroot_registrar",
            "--path", *todo,
            "--phase", "0.5",
        ]
        cp = subprocess.run(cmd, capture_output=True, text=True)
        print("[audit] registrar output:\n" + (cp.stdout or cp.stderr))

    payload_done = {
        "missing_manifest": missing_manifest,
        "missing_history": missing_history,
        "missing_devlist": missing_devlist,
        "auto_fixed": bool(args.auto_fix),
    }
    log_memory_event("manifest_history_auditor done", source=src, tags=["tool", "manifest", "history", "done"], content=payload_done, phase=REQUIRED_PHASE)
    log_trace_event("manifest_history_auditor done", source=src, tags=["tool", "manifest", "history", "done"], content=payload_done, phase=REQUIRED_PHASE)

if __name__ == "__main__":
    run_cli()

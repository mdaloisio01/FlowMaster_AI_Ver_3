# -*- coding: utf-8 -*-
# tools/phase_0_5_sealer.py
# Phase 0.5 sealer:
# - Runs the official seal check chain (fail-closed on any issue)
# - On success, bumps manifest current_phase -> 0.6 and appends build log entry
# - Accepts current_phase 0.4 or 0.5 (typical before sealing 0.5)
# - IronRoot rules: path injection first, phase lock, dual logging, UTF-8 JSON, forward slashes

from boot.boot_path_initializer import inject_paths
inject_paths()

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

# Phase lock imports (scanner looks for this exact form)
from core.phase_control import ensure_phase, REQUIRED_PHASE
from core.phase_control import get_current_phase

from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event

MANIFEST_PATH = Path("configs/ironroot_manifest_data.json")
BUILD_LOG_PATH = Path("configs/phase_build_log.md")


def _run_cmd(module: str, args: List[str]) -> Tuple[int, str]:
    cmd = [sys.executable, "-m", module] + args
    proc = subprocess.run(cmd, capture_output=True, text=True)
    brief = (proc.stdout or proc.stderr or "").strip()
    return proc.returncode, brief[:3000]


def _now_iso() -> str:
    import time
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise RuntimeError(f"IRONROOT VIOLATION — Manifest missing. Path/Artifact: {path.as_posix()}. Build cannot proceed.")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"IRONROOT VIOLATION — Manifest not valid JSON ({e}). Path/Artifact: {path.as_posix()}. Build cannot proceed.")


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")


def _append_build_log(line: str) -> None:
    if not BUILD_LOG_PATH.parent.exists():
        BUILD_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    prev = BUILD_LOG_PATH.read_text(encoding="utf-8") if BUILD_LOG_PATH.exists() else ""
    if prev and not prev.endswith("\n"):
        prev += "\n"
    BUILD_LOG_PATH.write_text(prev + line + "\n", encoding="utf-8", newline="\n")


def run_cli() -> None:
    # === Phase enforcement (scanner expects these lines) ===
    ensure_phase()
    current_phase = get_current_phase()
    if current_phase != REQUIRED_PHASE:
        raise RuntimeError(f"IRONROOT VIOLATION — Phase mismatch. Required: {REQUIRED_PHASE}, Current: {current_phase}")

    parser = argparse.ArgumentParser(description="Phase 0.5 Sealer", allow_abbrev=False)
    parser.add_argument("--dry-run", action="store_true", help="Run checks but do not write manifest/log.")
    args = parser.parse_args()

    # Dual logging start
    payload = {"ts": _now_iso(), "phase_expected": float(REQUIRED_PHASE), "dry_run": bool(args.dry_run)}
    src = __file__.replace("\\", "/")
    log_memory_event("phase_0_5_sealer start", source=src, tags=["tool", "seal", "phase"], content=payload, phase=REQUIRED_PHASE)
    log_trace_event("phase_0_5_sealer start", source=src, tags=["tool", "seal", "phase"], content=payload, phase=REQUIRED_PHASE)

    # Ordered seal checks (per spec)
    steps = [
        ("core.sqlite_bootstrap", []),
        ("tools.check_db_tables", []),
        ("tests.test_phase_0_5_trace_memory_integrity", []),
        ("tests.test_phase_0_5_snapshot_diffs", []),
        ("tools.tools_check_utf8_encoding", []),
        ("tools.trace_inspector", ["--tag", "snapshot"]),
        ("tools.trace_memory_crosscheck", []),
        ("tools.db_snapshot_auditor", []),
        ("tools.reflex_compliance_guard", []),
    ]

    for mod, mod_args in steps:
        code, brief = _run_cmd(mod, mod_args)
        if code != 0:
            reason = f"Seal step failed: py -m {mod} {' '.join(mod_args)} ⇒ exit={code}; out='{brief}'"
            raise RuntimeError(f"IRONROOT VIOLATION — {reason}. Path/Artifact: tools/phase_0_5_sealer.py. Build cannot proceed.")

    # All checks passed — update manifest + log
    if not args.dry_run:
        mani = _read_json(MANIFEST_PATH)

        if "current_phase" not in mani:
            raise RuntimeError(f"IRONROOT VIOLATION — current_phase missing in manifest. Path/Artifact: {MANIFEST_PATH.as_posix()}. Build cannot proceed.")

        cur_str = str(mani["current_phase"]).strip()
        try:
            cur_val = float(cur_str)
        except Exception:
            raise RuntimeError(f"IRONROOT VIOLATION — Unparseable current_phase='{cur_str}'. Path/Artifact: {MANIFEST_PATH.as_posix()}. Build cannot proceed.")

        if cur_val < 0.4:
            raise RuntimeError(f"IRONROOT VIOLATION — Phase mismatch (current_phase={cur_str} < 0.4). Path/Artifact: {MANIFEST_PATH.as_posix()}. Build cannot proceed.")

        if cur_val >= 0.6:
            _append_build_log(f"{_now_iso()} — Phase 0.5 seal checks re-run; manifest already at {cur_str}; no bump.")
        else:
            mani["current_phase"] = 0.6
            history = mani.setdefault("phase_history", [])
            history.append({"ts": _now_iso(), "from": cur_str, "to": "0.6", "note": "Phase 0.5 complete"})
            _write_json(MANIFEST_PATH, mani)
            _append_build_log(f"{_now_iso()} — Phase 0.5 complete — all seal checks green; manifest bumped {cur_str} → 0.6")

    # Dual logging done
    done = {"ts": _now_iso(), "bumped_to": "0.6", "dry_run": bool(args.dry_run)}
    log_memory_event("phase_0_5_sealer done", source=src, tags=["tool", "seal", "phase"], content=done, phase=REQUIRED_PHASE)
    log_trace_event("phase_0_5_sealer done", source=src, tags=["tool", "seal", "phase"], content=done, phase=REQUIRED_PHASE)

    print("[sealer] Phase 0.5 seal checks passed; manifest updated to current_phase=0.6" if not args.dry_run else "[sealer] Dry run OK")


if __name__ == "__main__":
    run_cli()

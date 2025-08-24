# tools/ironroot_registrar.py
# Registers files into:
#   - configs/ironroot_manifest_data.json
#   - configs/ironroot_file_history_with_dependencies.json
#   - configs/dev_file_list.md
#
# IronRoot rules: path injection first, phase lock, dual logging, UTF-8, forward slashes.

from boot.boot_path_initializer import inject_paths
inject_paths()

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple

from core.phase_control import ensure_phase, REQUIRED_PHASE
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event

# ---- constants ----

MANIFEST_PATH = Path("configs/ironroot_manifest_data.json")
HISTORY_PATH = Path("configs/ironroot_file_history_with_dependencies.json")
DEVLIST_PATH = Path("configs/dev_file_list.md")

# Default Phase 0.5 artifacts to register (alpha-sorted)
DEFAULT_FILES = [
    "core/snapshot_manager.py",
    "reflexes/reflex_core/reflex_table_tick.py",
    "reflexes/reflex_core/reflex_trace_ping.py",
    "tests/test_phase_0_5_snapshot_diffs.py",
    "tests/test_phase_0_5_trace_memory_integrity.py",
    "tools/db_snapshot_auditor.py",
    "tools/trace_memory_crosscheck.py",
    "tools/trace_memory_snapshot.py",
]

# Dependencies per file (forward slashes). Conservative (safe) graph.
COMMON_DEPS = [
    "core/phase_control.py",
    "core/sqlite_bootstrap.py",
    "core/memory_interface.py",
    "core/trace_logger.py",
]

FILE_DEPS: Dict[str, List[str]] = {
    "core/snapshot_manager.py": ["core/sqlite_bootstrap.py"],
    "reflexes/reflex_core/reflex_table_tick.py": COMMON_DEPS,
    "reflexes/reflex_core/reflex_trace_ping.py": [
        "core/phase_control.py",
        "core/memory_interface.py",
        "core/trace_logger.py",
    ],
    "tests/test_phase_0_5_snapshot_diffs.py": [
        "core/phase_control.py",
        "core/sqlite_bootstrap.py",
        "tools/trace_memory_snapshot.py",
    ],
    "tests/test_phase_0_5_trace_memory_integrity.py": [
        "core/phase_control.py",
        "tools/trace_memory_snapshot.py",
        "tools/trace_memory_crosscheck.py",
    ],
    "tools/db_snapshot_auditor.py": COMMON_DEPS,
    "tools/trace_memory_crosscheck.py": COMMON_DEPS,
    "tools/trace_memory_snapshot.py": COMMON_DEPS + ["core/snapshot_manager.py"],
}

# ---- helpers ----

def _read_json(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    return json.loads(text)

def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")

def _alpha_unique(seq: List[str]) -> List[str]:
    return sorted(sorted(set(seq)), key=lambda s: s.lower())

def _category_for(path: str) -> str:
    # first segment before slash
    return path.split("/", 1)[0] if "/" in path else "root"

def _ensure_manifest_lists(mani: dict) -> None:
    mani.setdefault("manifest", {})
    for k in ["core", "reflexes", "tools", "sandbox", "tests", "configs", "seeds", "all_files"]:
        mani["manifest"].setdefault(k, [])
    mani.setdefault("files", [])

def _register_manifest(mani: dict, files: List[str]) -> Tuple[int, int]:
    _ensure_manifest_lists(mani)
    added_cats = 0
    added_all = 0
    for f in files:
        cat = _category_for(f)
        # Put unknown categories under 'configs' if they are configs, else under 'all_files' only
        target_list = mani["manifest"].get(cat)
        if target_list is None:
            target_list = mani["manifest"].setdefault(cat, [])
        before = len(target_list)
        target_list = list(target_list) + [f]
        mani["manifest"][cat] = _alpha_unique(target_list)
        added_cats += int(len(mani["manifest"][cat]) > before)

        # all_files + top-level files
        mani["manifest"]["all_files"] = _alpha_unique(list(mani["manifest"]["all_files"]) + [f])
        mani["files"] = _alpha_unique(list(mani["files"]) + [f])
        added_all += 1
    return added_cats, added_all

def _register_history(hist: dict, files: List[str], phase: float) -> int:
    hist.setdefault("history", {})
    count = 0
    for f in files:
        if f not in hist["history"]:
            deps = FILE_DEPS.get(f, [])
            hist["history"][f] = {"phase": phase, "dependencies": deps}
            count += 1
    # maintain alpha key order by rewriting
    ordered = {k: hist["history"][k] for k in _alpha_unique(list(hist["history"].keys()))}
    hist["history"] = ordered
    return count

def _register_devlist(devlist_path: Path, files: List[str]) -> int:
    if devlist_path.exists():
        lines = [ln.strip() for ln in devlist_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    else:
        lines = []
    before = set(lines)
    lines = _alpha_unique(lines + files)
    devlist_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return len(set(lines) - before)

def run_cli() -> None:
    ensure_phase()

    parser = argparse.ArgumentParser(description="IronRoot Registrar", allow_abbrev=False)
    parser.add_argument("--files-json", default=None,
                        help="JSON array of file paths to register. If omitted, registers Phase 0.5 defaults.")
    parser.add_argument("--phase", default="0.5", help="Phase number to record in history (default: 0.5).")
    parser.add_argument("--apply", action="store_true", help="Apply changes (writes to files).")
    args = parser.parse_args()

    # Determine file list
    if args.files_json:
        try:
            files = json.loads(args.files_json)
            if not isinstance(files, list) or not all(isinstance(x, str) for x in files):
                raise ValueError
        except Exception:
            raise RuntimeError("--files-json must be a JSON array of strings.")
    else:
        files = DEFAULT_FILES[:]

    # Normalize paths to forward slashes and alpha-sort
    files = _alpha_unique([p.replace("\\", "/") for p in files])

    # Log start
    payload = {"files": files, "phase": args.phase, "apply": bool(args.apply)}
    src = __file__.replace("\\", "/")
    log_memory_event("ironroot_registrar start", source=src, tags=["tool", "manifest", "history"],
                     content=payload, phase=REQUIRED_PHASE)
    log_trace_event("ironroot_registrar start", source=src, tags=["tool", "manifest", "history"],
                    content=payload, phase=REQUIRED_PHASE)

    # Load current configs
    mani = _read_json(MANIFEST_PATH)
    hist = _read_json(HISTORY_PATH)

    # Apply registrations (in-memory first)
    _ensure_manifest_lists(mani)
    cats_added, all_added = _register_manifest(mani, files)
    hist_added = _register_history(hist, files, float(args.phase))
    dev_added = _register_devlist(DEVLIST_PATH, files) if args.apply else 0  # only write dev list on apply; preview prints planned adds

    # Write if --apply
    if args.apply:
        _write_json(MANIFEST_PATH, mani)
        _write_json(HISTORY_PATH, hist)

    # Summary
    print(f"[registrar] files={len(files)} preview={'no' if args.apply else 'yes'}")
    print(f"[registrar] manifest: categories_touched≈{cats_added}, all_files+files_added={all_added}")
    print(f"[registrar] history: new_entries={hist_added}")
    if args.apply:
        print(f"[registrar] dev_file_list: new_lines={dev_added}")

    # Log done
    done_payload = {
        "applied": bool(args.apply),
        "manifest_cats_touched": cats_added,
        "manifest_files_added": all_added,
        "history_added": hist_added,
        "dev_list_added": dev_added if args.apply else None,
    }
    log_memory_event("ironroot_registrar done", source=src, tags=["tool", "manifest", "history"],
                     content=done_payload, phase=REQUIRED_PHASE)
    log_trace_event("ironroot_registrar done", source=src, tags=["tool", "manifest", "history"],
                    content=done_payload, phase=REQUIRED_PHASE)

if __name__ == "__main__":
    run_cli()

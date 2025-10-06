# tools/ironroot_registrar.py
# Registrar for IronRoot configs (manifest, dev_file_list, file history)
# - Provides register_path() and CLI
# - UTF-8 writes; forward slashes; dual logging; phase lock
from boot.boot_path_initializer import inject_paths
inject_paths()

import argparse, json, os, sys, time
from pathlib import Path
from typing import List, Optional, Dict, Any

from core.phase_control import REQUIRED_PHASE, ensure_phase
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event

CFG_MANIFEST = Path("configs/ironroot_manifest_data.json")
CFG_DEVLIST  = Path("configs/dev_file_list.md")
CFG_HISTORY  = Path("configs/ironroot_file_history_with_dependencies.json")

def _now_utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def _norm(p: str) -> str:
    return p.replace("\\", "/")

def _read_json(p: Path) -> Any:
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))

def _write_json(p: Path, data: Any) -> None:
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

def _ensure_manifest_has(files: List[str]) -> bool:
    changed = False
    data = _read_json(CFG_MANIFEST) or {}
    arr = data.setdefault("files", [])
    for f in files:
        if f not in arr:
            arr.append(f)
            changed = True
    data["files"] = sorted(set(arr), key=lambda s: s)
    if changed:
        _write_json(CFG_MANIFEST, data)
    return changed

def _ensure_devlist_has(files: List[str]) -> bool:
    existing = CFG_DEVLIST.read_text(encoding="utf-8") if CFG_DEVLIST.exists() else ""
    changed = False
    tail: List[str] = []
    for f in files:
        if f not in existing:
            tail.append(f"- {f}")
            changed = True
    if changed:
        block = []
        block.append("")
        block.append("<!-- auto:ironroot_registrar -->")
        block.extend(tail)
        text = existing + ("\n" if existing and not existing.endswith("\n") else "") + "\n".join(block) + "\n"
        CFG_DEVLIST.write_text(text, encoding="utf-8", newline="\n")
    return changed

def _ensure_history_has(files: List[str], phase_value: Optional[float], deps: Optional[List[str]]) -> bool:
    changed = False
    data = _read_json(CFG_HISTORY)
    if not data:
        data = {"history": {}}
    # Auditor expects dict form {"history": {path: {...}}}
    if isinstance(data.get("history"), list):
        # normalize any legacy list into dict
        hist_dict = {}
        for e in data["history"]:
            if isinstance(e, dict) and "path" in e:
                hist_dict[e["path"]] = {k: e.get(k) for k in ("phase","deps","ts","note")}
        data["history"] = hist_dict
    elif not isinstance(data.get("history"), dict):
        data["history"] = {}

    hist: Dict[str, Any] = data["history"]
    phase_str = str(phase_value if phase_value is not None else REQUIRED_PHASE)
    ts = _now_utc()
    deps = deps or []

    for f in files:
        entry = hist.get(f)
        if not isinstance(entry, dict):
            hist[f] = {"phase": phase_str, "deps": deps, "ts": ts, "note": "auto-registered"}
            changed = True
        else:
            upd = False
            if "phase" not in entry: entry["phase"] = phase_str; upd = True
            if "deps"  not in entry: entry["deps"]  = deps;       upd = True
            if "ts"    not in entry: entry["ts"]    = ts;         upd = True
            if upd: changed = True

    if changed:
        _write_json(CFG_HISTORY, data)
    return changed

def register_path(path: str, *, phase: Optional[float] = None, deps: Optional[List[str]] = None) -> Dict[str, Any]:
    """Register a single path across manifest, dev list, and file history."""
    ensure_phase(REQUIRED_PHASE)
    p = _norm(path)
    run_id = f"registrar:{p}"
    log_memory_event("registrar:start", source=__file__, tags=["tool","start"], phase=REQUIRED_PHASE, content={"run_id":run_id,"path":p})
    log_trace_event("registrar:start", source=__file__, tags=["tool","start"], phase=REQUIRED_PHASE, content={"run_id":run_id,"path":p})

    changed_any = False
    changed_any |= _ensure_manifest_has([p])
    changed_any |= _ensure_devlist_has([p])
    changed_any |= _ensure_history_has([p], phase, deps)

    result = {"path": p, "changed": changed_any, "phase": str(phase if phase is not None else REQUIRED_PHASE)}
    log_memory_event("registrar:report", source=__file__, tags=["tool","report"], phase=REQUIRED_PHASE, content={"run_id":run_id,"result":result})
    log_trace_event("registrar:done", source=__file__, tags=["tool","done"], phase=REQUIRED_PHASE, content={"run_id":run_id})
    return result

def register_paths(paths: List[str], *, phase: Optional[float] = None, deps: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    ensure_phase(REQUIRED_PHASE)
    results = []
    for p in sorted({_norm(x) for x in paths}):
        results.append(register_path(p, phase=phase, deps=deps))
    return results

def main():
    ensure_phase(REQUIRED_PHASE)
    ap = argparse.ArgumentParser(description="IronRoot registrar for manifest/devlist/history.")
    ap.add_argument("--path", dest="paths", action="append", help="File path to register (repeatable).")
    ap.add_argument("--files-json", type=str, default=None, help="JSON array of file paths to register.")
    ap.add_argument("--phase", type=float, default=None, help="Phase value to record (defaults to REQUIRED_PHASE).")
    ap.add_argument("--deps", type=str, default="", help="Comma-separated dependency paths.")
    ap.add_argument("--apply", action="store_true", help="Apply changes (for hooks).")
    args = ap.parse_args()

    paths = [p for p in (args.paths or []) if p]
    if args.files_json:
        try:
            paths.extend(list(json.loads(args.files_json)))
        except Exception as e:
            print(f"--files-json parse error: {e}", file=sys.stderr)
            sys.exit(2)

    if not paths:
        print("No paths provided.", file=sys.stderr)
        sys.exit(2)

    deps = [d for d in args.deps.split(",") if d] if args.deps else None

    # In IronRoot, registrar always applies; --apply exists to satisfy hooks.
    out = register_paths(paths, phase=args.phase, deps=deps)
    for r in out:
        print(f"{r['path']} -> {'changed' if r['changed'] else 'ok'} (phase {r['phase']})")

if __name__ == "__main__":
    main()

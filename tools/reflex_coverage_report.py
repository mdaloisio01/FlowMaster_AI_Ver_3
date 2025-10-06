# tools/reflex_coverage_report.py
# TraceSync Coverage (CLI ↔ Reflex parity)
# - Path injection FIRST
# - Phase lock via ensure_phase()
# - Dual logging triplets (start → report → done) in BOTH memory & trace with shared run_id
# - UTF-8 JSON output; forward slashes
# - Uses BOTH DB manifest and configs/ironroot_manifest_data.json as sources of truth

from boot.boot_path_initializer import inject_paths
inject_paths()

import argparse
import ast
import json
import os
import uuid
from pathlib import Path
from typing import Any, Dict, List, Set

from core.phase_control import ensure_phase, REQUIRED_PHASE
from core.sqlite_bootstrap import DB_PATH
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event

# ---------------- helpers ----------------

def _read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

def _is_cli_like(src: str) -> bool:
    return ("def run_cli" in src) or ("argparse" in src)

def _has_main_guard(src: str) -> bool:
    return ("if __name__ == \"__main__\":" in src) or ("if __name__ == '__main__':" in src)

def _has_phase_import(src: str) -> bool:
    return "from core.phase_control import" in src

def _calls_ensure_phase(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            if getattr(f, "id", None) == "ensure_phase":
                return True
            if getattr(f, "attr", None) == "ensure_phase":
                return True
    return False

def _uses_loggers(src: str) -> Dict[str, bool]:
    return {"logs_memory": ("log_memory_event" in src), "logs_trace": ("log_trace_event" in src)}

def _rel(p: Path) -> str:
    return p.as_posix()

def _discover_reflex_files() -> List[Path]:
    base = Path("reflexes")
    if not base.exists():
        return []
    return sorted([p for p in base.rglob("*.py") if "__pycache__" not in p.parts])

def _infer_reflex_name(p: Path) -> str:
    return p.stem

def _load_history_paths() -> Set[str]:
    hist_p = Path("configs/ironroot_file_history_with_dependencies.json")
    out: Set[str] = set()
    try:
        raw = json.loads(hist_p.read_text(encoding="utf-8"))
        if isinstance(raw, dict) and "history" in raw and isinstance(raw["history"], dict):
            out = {str(k).replace("\\", "/") for k in raw["history"].keys()}
    except Exception:
        pass
    return out

def _fetch_manifest_db_paths() -> Set[str]:
    try:
        from core.manifest_db import fetch_all_manifest
        rows = fetch_all_manifest()
        return {str((r.get("path") or "")).replace("\\", "/") for r in rows if isinstance(r, dict)}
    except Exception:
        return set()

def _load_manifest_cfg_paths() -> Set[str]:
    cfg_p = Path("configs/ironroot_manifest_data.json")
    out: Set[str] = set()
    try:
        data = json.loads(cfg_p.read_text(encoding="utf-8"))
        man = data.get("manifest", {})
        if isinstance(man, dict):
            for _, arr in man.items():
                if isinstance(arr, list):
                    for p in arr:
                        out.add(str(p).replace("\\", "/"))
    except Exception:
        pass
    return out

# ---------------- main ----------------

def run_cli() -> None:
    ensure_phase()  # lock to REQUIRED_PHASE

    parser = argparse.ArgumentParser(
        description="TraceSync Coverage (CLI ↔ Reflex parity)",
        allow_abbrev=False,
    )
    parser.add_argument("--assert", dest="assert_mode", action="store_true", help="Exit non-zero if any coverage cell is false.")
    parser.add_argument("--print-report", action="store_true", help="Print detailed per-reflex rows.")
    args = parser.parse_args()

    tool = Path(__file__).as_posix()
    run_id = os.environ.get("RUN_ID") or f"reflex_coverage_report:{REQUIRED_PHASE}:{uuid.uuid4()}"

    # Start (dual logging)
    log_memory_event(
        event_text="reflex_coverage_report start",
        source=tool,
        tags=["tool","coverage","start"],
        content={"run_id": run_id, "db": Path(DB_PATH).as_posix()},
        phase=REQUIRED_PHASE,
    )
    log_trace_event(
        description="reflex_coverage_report start",
        source=tool,
        tags=["tool","coverage","start"],
        content={"run_id": run_id},
        phase=REQUIRED_PHASE,
    )

    # Sources of truth
    file_history_paths = _load_history_paths()
    manifest_db_paths = _fetch_manifest_db_paths()
    manifest_cfg_paths = _load_manifest_cfg_paths()
    manifest_union = manifest_db_paths.union(manifest_cfg_paths)

    # Reflex discovery
    files = _discover_reflex_files()
    rows: List[Dict[str, Any]] = []

    for p in files:
        rel = _rel(p)
        src = _read_text(p)
        try:
            tree = ast.parse(src)
        except Exception:
            tree = ast.parse("")

        name = _infer_reflex_name(p)
        props = _uses_loggers(src)

        row = {
            "reflex_name": name,
            "path": rel,
            "registered_in_manifest": (rel in manifest_union),  # DB or config manifest
            "listed_in_file_history": (rel in file_history_paths),
            "has_cli_binding": _is_cli_like(src) and _has_main_guard(src),
            "has_phase_lock": _has_phase_import(src) and _calls_ensure_phase(tree),
            "logs_memory": props["logs_memory"],
            "logs_trace": props["logs_trace"],
            "stubbed": False,
        }
        row["testable"] = bool(row["has_cli_binding"] and not row["stubbed"])
        rows.append(row)

    all_ok = all(
        r["registered_in_manifest"]
        and r["listed_in_file_history"]
        and r["has_cli_binding"]
        and r["has_phase_lock"]
        and r["logs_memory"]
        and r["logs_trace"]
        and (not r["stubbed"])
        and r["testable"]
        for r in rows
    )
    fail_count = sum(1 for r in rows if not (
        r["registered_in_manifest"]
        and r["listed_in_file_history"]
        and r["has_cli_binding"]
        and r["has_phase_lock"]
        and r["logs_memory"]
        and r["logs_trace"]
        and (not r["stubbed"])
        and r["testable"]
    ))

    totals = {"count": len(rows), "all_ok": all_ok, "fail_count": fail_count}

    # Report (dual logging)
    log_memory_event(
        event_text="reflex_coverage_report report",
        source=tool,
        tags=["tool","coverage","report"],
        content={"run_id": run_id, "totals": totals},
        phase=REQUIRED_PHASE,
    )
    log_trace_event(
        description="reflex_coverage_report report",
        source=tool,
        tags=["tool","coverage","report"],
        content={"run_id": run_id, "totals": totals},
        phase=REQUIRED_PHASE,
    )

    # Done (dual logging)
    log_memory_event(
        event_text="reflex_coverage_report done",
        source=tool,
        tags=["tool","coverage","done"],
        content={"run_id": run_id, "all_ok": all_ok},
        phase=REQUIRED_PHASE,
    )
    log_trace_event(
        description="reflex_coverage_report done",
        source=tool,
        tags=["tool","coverage","done"],
        content={"run_id": run_id, "all_ok": all_ok},
        phase=REQUIRED_PHASE,
    )

    # Console output
    if args.print_report:
        print(json.dumps({"rows": rows, "totals": totals}, ensure_ascii=False, indent=2))
    print(f"[coverage] reflexes={totals['count']} all_ok={totals['all_ok']} fails={totals['fail_count']}")

    if args.assert_mode and (not all_ok):
        raise SystemExit(1)

if __name__ == "__main__":
    run_cli()

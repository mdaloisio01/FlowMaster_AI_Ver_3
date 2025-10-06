# tools/db_schema_contract.py
from boot.boot_path_initializer import inject_paths
inject_paths()

import argparse, json, sqlite3, sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
from core.phase_control import REQUIRED_PHASE, ensure_phase
from core.sqlite_bootstrap import DB_PATH, ensure_tables
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event

# Contract = minimum required columns, but may include legacy columns so earlier code keeps working.
CONTRACT: Dict[str, Dict[str, Any]] = {
    "boot_events": {"columns": ["id","ts","event","details"]},
    "manifest": {"columns": ["id","path","added_ts","phase"], "unique": ["path"]},
    "memory_events": {"columns": ["id","ts","tag","payload"]},
    "reflex_registry": {"columns": ["id","ts","reflex_name","module","path","enabled"]},
    "trace_events": {"columns": ["id","ts","level","tag","message","context"]},
    # Include BOTH the 0.6 contract shape and legacy fields used by snapshot_manager
    "snapshot_index": {"columns": [
        "id","ts","run_id","mode","tables_changed",          # 0.6 canonical
        "snapshot_id","created_at","pre_checksum","post_checksum","run_dir","status"  # legacy in use
    ]},
    "test_ticks": {"columns": ["id","ts","tick"]},
    "schema_migrations": {"columns": ["version","applied_at","details"]},
}

def _connect() -> sqlite3.Connection:
    ensure_tables()
    return sqlite3.connect(Path(DB_PATH).as_posix())

def audit_schema(conn: sqlite3.Connection) -> Tuple[bool, Dict[str, Any]]:
    report: Dict[str, Any] = {}
    ok_all = True
    for table, spec in CONTRACT.items():
        t_info = {"present": False, "missing_columns": [], "extra_columns": [], "has_unique": []}
        # detect table
        try:
            cols = conn.execute(f"PRAGMA table_info({table});").fetchall()
        except sqlite3.Error:
            cols = []
        if cols:
            t_info["present"] = True
            have = [c[1] for c in cols]
            need = spec.get("columns", [])
            t_info["missing_columns"] = [c for c in need if c not in have]
            t_info["extra_columns"] = [c for c in have if c not in need]
            # unique detection (best-effort)
            wanted_uniques = set(spec.get("unique", []))
            if wanted_uniques:
                try:
                    idx_list = conn.execute(f"PRAGMA index_list({table});").fetchall()
                    uniques = set()
                    for row in idx_list:
                        # row: (seq, name, unique, origin, partial)
                        name = row[1]; unique = row[2]
                        if unique:
                            cols_idx = conn.execute(f"PRAGMA index_info({name});").fetchall()
                            for _,_,col in cols_idx:
                                uniques.add(col)
                    t_info["has_unique"] = sorted(list(uniques & wanted_uniques))
                except sqlite3.Error:
                    t_info["has_unique"] = []
        else:
            t_info["present"] = False
            t_info["missing_columns"] = spec.get("columns", [])
        # final
        table_ok = t_info["present"] and not t_info["missing_columns"]
        if spec.get("unique"):
            table_ok = table_ok and set(spec["unique"]).issubset(set(t_info["has_unique"]))
        ok_all = ok_all and table_ok
        report[table] = t_info
    return ok_all, report

def main():
    ensure_phase(REQUIRED_PHASE)
    ap = argparse.ArgumentParser()
    ap.add_argument("--assert", dest="do_assert", action="store_true", help="Non-zero exit if mismatch.")
    ap.add_argument("--print-report", action="store_true")
    args = ap.parse_args()

    run_id = "db_schema_contract"
    log_memory_event("db_schema_contract:start", source=__file__, tags=["tool","start"], phase=REQUIRED_PHASE, content={"run_id":run_id})
    log_trace_event("db_schema_contract:start", source=__file__, tags=["tool","start"], phase=REQUIRED_PHASE, content={"run_id":run_id})

    with _connect() as con:
        ok, report = audit_schema(con)

    if args.print_report:
        print(json.dumps(report, ensure_ascii=False, indent=2))

    log_memory_event("db_schema_contract:report", source=__file__, tags=["tool","report"], phase=REQUIRED_PHASE, content={"run_id":run_id,"ok":ok})
    log_trace_event("db_schema_contract:done", source=__file__, tags=["tool","done"], phase=REQUIRED_PHASE, content={"run_id":run_id})

    if args.do_assert and not ok:
        sys.exit(1)

if __name__ == "__main__":
    main()

# tools/db_schema_migrate.py
from boot.boot_path_initializer import inject_paths
inject_paths()

import argparse, json, sqlite3, sys, time
from pathlib import Path
from typing import Dict, Any, List
from core.phase_control import REQUIRED_PHASE, ensure_phase
from core.sqlite_bootstrap import DB_PATH, ensure_tables
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event
from tools.db_schema_contract import CONTRACT, audit_schema

def _connect() -> sqlite3.Connection:
    ensure_tables()
    return sqlite3.connect(Path(DB_PATH).as_posix())

def _ensure_schema_migrations(con: sqlite3.Connection) -> None:
    con.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL,
            details TEXT
        )
    """)

def _add_columns(con: sqlite3.Connection, table: str, missing: List[str]) -> List[str]:
    applied = []
    for col in missing:
        try:
            con.execute(f"ALTER TABLE {table} ADD COLUMN {col} TEXT")
            applied.append(f"ALTER {table} ADD {col}")
        except sqlite3.Error as e:
            applied.append(f"[WARN] {table} ADD {col} failed: {e}")
    return applied

def _table_info(con: sqlite3.Connection, table: str):
    return con.execute(f"PRAGMA table_info({table});").fetchall()  # (cid,name,type,notnull,dflt,pk)

def _maybe_rebuild_snapshot_index_ts_default(con: sqlite3.Connection) -> List[str]:
    """Ensure snapshot_index.ts has a DEFAULT so inserts that omit ts won't violate NOT NULL."""
    steps: List[str] = []
    try:
        cols = _table_info(con, "snapshot_index")
    except sqlite3.Error:
        return steps
    if not cols:
        return steps
    ts_meta = None
    for _, name, ctype, notnull, dflt_value, pk in cols:
        if name == "ts":
            ts_meta = (ctype or "TEXT", int(notnull), dflt_value, int(pk))
            break
    if ts_meta is None:
        return steps
    _, notnull, dflt_value, _ = ts_meta
    if notnull == 1 and dflt_value is None:
        con.execute("""
            CREATE TABLE IF NOT EXISTS __new_snapshot_index (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                run_id TEXT,
                mode TEXT,
                tables_changed TEXT,
                snapshot_id TEXT,
                created_at TEXT,
                pre_checksum TEXT,
                post_checksum TEXT,
                run_dir TEXT,
                status TEXT
            );
        """)
        con.execute("""
            INSERT INTO __new_snapshot_index
            (id, ts, run_id, mode, tables_changed, snapshot_id, created_at, pre_checksum, post_checksum, run_dir, status)
            SELECT
                id,
                COALESCE(ts, CURRENT_TIMESTAMP),
                run_id,
                mode,
                tables_changed,
                snapshot_id,
                created_at,
                pre_checksum,
                post_checksum,
                run_dir,
                status
            FROM snapshot_index;
        """)
        con.execute("DROP TABLE snapshot_index;")
        con.execute("ALTER TABLE __new_snapshot_index RENAME TO snapshot_index;")
        steps.append("REBUILD snapshot_index (ts DEFAULT CURRENT_TIMESTAMP)")
    return steps

def apply_migrations(conn: sqlite3.Connection, contract: Dict[str, Dict[str, Any]]) -> List[str]:
    steps: List[str] = []
    _ensure_schema_migrations(conn)

    ok, report = audit_schema(conn)
    for table, info in report.items():
        if not info["present"]:
            cols = contract[table]["columns"]
            ddl = []
            for c in cols:
                if c == "id":
                    ddl.append("id INTEGER PRIMARY KEY AUTOINCREMENT")
                elif table == "schema_migrations" and c == "version":
                    ddl.append("version TEXT PRIMARY KEY")
                elif table == "snapshot_index" and c == "ts":
                    ddl.append("ts TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP")
                else:
                    ddl.append(f"{c} TEXT")
            conn.execute(f"CREATE TABLE IF NOT EXISTS {table} ({', '.join(ddl)});")
            steps.append(f"CREATE {table}")
            if table == "manifest":
                conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_manifest_path ON manifest(path);")
                steps.append("INDEX ux_manifest_path(path)")
            continue

        missing = info.get("missing_columns", [])
        if missing:
            steps += _add_columns(conn, table, missing)

        if table == "manifest":
            try:
                idx_list = conn.execute("PRAGMA index_list(manifest);").fetchall()
                has_unique = any(row[2] for row in idx_list)
                if not has_unique:
                    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_manifest_path ON manifest(path);")
                    steps.append("INDEX ux_manifest_path(path)")
            except sqlite3.Error:
                pass

        if table == "snapshot_index":
            steps += _maybe_rebuild_snapshot_index_ts_default(conn)

    if steps:
        version = f"0.6-{time.strftime('%Y%m%d%H%M%S', time.gmtime())}"
        details = json.dumps(steps, ensure_ascii=False)
        conn.execute(
            "INSERT OR REPLACE INTO schema_migrations (version, applied_at, details) VALUES (?, ?, ?);",
            (version, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), details),
        )
    conn.commit()
    return steps

def main():
    ensure_phase(REQUIRED_PHASE)
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--reason", type=str, default="")
    args = ap.parse_args()

    run_id = "db_schema_migrate"
    log_memory_event("db_schema_migrate:start", source=__file__, tags=["tool","start"], phase=REQUIRED_PHASE, content={"run_id":run_id,"reason":args.reason})
    log_trace_event("db_schema_migrate:start", source=__file__, tags=["tool","start"], phase=REQUIRED_PHASE, content={"run_id":run_id,"reason":args.reason})

    with _connect() as con:
        if args.apply:
            steps = apply_migrations(con, CONTRACT)
            print("\n".join(steps) if steps else "No changes.")
        else:
            ok, report = audit_schema(con)
            print("OK" if ok else json.dumps(report, ensure_ascii=False, indent=2))

    log_memory_event("db_schema_migrate:report", source=__file__, tags=["tool","report"], phase=REQUIRED_PHASE, content={"run_id":run_id})
    log_trace_event("db_schema_migrate:done", source=__file__, tags=["tool","done"], phase=REQUIRED_PHASE, content={"run_id":run_id})

if __name__ == "__main__":
    main()

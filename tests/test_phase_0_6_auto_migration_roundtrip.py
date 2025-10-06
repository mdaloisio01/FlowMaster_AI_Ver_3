# tests/test_phase_0_6_auto_migration_roundtrip.py
from boot.boot_path_initializer import inject_paths
inject_paths()

import sqlite3, json, time
from pathlib import Path
from core.phase_control import REQUIRED_PHASE, ensure_phase
from core.sqlite_bootstrap import DB_PATH, ensure_tables
from core.manifest_db import upsert_manifest_path, fetch_all_manifest

def test_roundtrip_and_schema_migrations_row():
    ensure_phase(REQUIRED_PHASE)
    ensure_tables()

    # Apply migrations
    import subprocess, sys
    res = subprocess.run([sys.executable, "-m", "tools.db_schema_migrate", "--apply", "--reason", "phase_0_6_test"], capture_output=True, text=True)
    assert res.returncode == 0, res.stderr

    # We expect schema_migrations to exist and contain at least one row historically (creation or prior)
    with sqlite3.connect(Path(DB_PATH).as_posix()) as con:
        con.execute("""CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL,
            details TEXT
        );""")
        rows = con.execute("SELECT COUNT(*) FROM schema_migrations;").fetchone()[0]
        assert rows >= 1

    # Roundtrip write/read manifest
    upsert_manifest_path("tools/db_schema_migrate.py", phase=REQUIRED_PHASE, added_ts=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    manifest_rows = fetch_all_manifest()
    assert any(r["path"].endswith("tools/db_schema_migrate.py") for r in manifest_rows)

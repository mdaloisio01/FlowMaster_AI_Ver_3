# tests/test_phase_0_5_snapshot_diffs.py
# Verifies snapshot engine captures a real DB change.

from boot.boot_path_initializer import inject_paths
inject_paths()

import json
import sqlite3
import sys
from pathlib import Path

from core.phase_control import ensure_phase
from core.sqlite_bootstrap import DB_PATH

# We will call the wrapper as a module so it performs pre/post + diff.
def _run_wrapper(module: str):
    # Simulate: py -m tools.trace_memory_snapshot --module <module> --snapshot-mode heavy
    import tools.trace_memory_snapshot as wrapper
    import importlib, argparse

    # Patch sys.argv for the wrapper's argparse
    argv_backup = sys.argv[:]
    sys.argv = ["trace_memory_snapshot.py", "--module", module, "--snapshot-mode", "heavy"]
    try:
        wrapper.run_cli()
    finally:
        sys.argv = argv_backup


def _latest_snapshot_index_row():
    import sqlite3
    from datetime import datetime

    with sqlite3.connect(Path(DB_PATH).as_posix()) as conn:
        # snapshot_index: (snapshot_id, run_id, created_at, pre_checksum, post_checksum, run_dir, status)
        cur = conn.execute(
            "SELECT snapshot_id, run_id, created_at, run_dir, status FROM snapshot_index ORDER BY rowid DESC LIMIT 1;"
        )
        row = cur.fetchone()
        if not row:
            raise AssertionError("No entries in snapshot_index; did the wrapper run?")
        return {
            "snapshot_id": row[0],
            "run_id": row[1],
            "created_at": row[2],
            "run_dir": row[3],
            "status": row[4],
        }


def test_snapshot_detects_table_change():
    ensure_phase()

    # Run a reflex that makes a guaranteed DB change.
    _run_wrapper("reflexes.reflex_core.reflex_table_tick")

    idx = _latest_snapshot_index_row()
    run_dir = Path(idx["run_dir"])
    diff_path = run_dir / "diff" / "report.json"

    assert diff_path.exists(), f"diff report missing at {diff_path}"
    summary = json.loads(diff_path.read_text(encoding="utf-8"))

    # Expect test_ticks to show up as changed (added row at least)
    changed_tables = set(summary.get("tables_changed", []))
    assert "test_ticks" in changed_tables, f"Expected 'test_ticks' in changed tables, got: {changed_tables}"

    # Minimal sanity
    assert idx["status"] == "ok"

# tools/db_snapshot_auditor.py
# Audits the latest (or specified) run's pre/post snapshot diff and logs results.

from boot.boot_path_initializer import inject_paths
inject_paths()

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Optional

from core.phase_control import ensure_phase, REQUIRED_PHASE
from core.sqlite_bootstrap import DB_PATH
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event


def _find_run_dir(run_id: Optional[str]) -> Path:
    with sqlite3.connect(Path(DB_PATH).as_posix()) as conn:
        if run_id:
            cur = conn.execute(
                "SELECT run_dir FROM snapshot_index WHERE run_id = ? ORDER BY rowid DESC LIMIT 1;",
                (run_id,),
            )
        else:
            cur = conn.execute(
                "SELECT run_dir FROM snapshot_index ORDER BY rowid DESC LIMIT 1;"
            )
        row = cur.fetchone()
        if not row:
            raise RuntimeError("No snapshot_index entries found. Run the snapshot wrapper first.")
        return Path(row[0])


def run_cli() -> None:
    ensure_phase()

    p = argparse.ArgumentParser(description="DB Snapshot Auditor", allow_abbrev=False)
    p.add_argument("--run-id", help="Audits a specific run_id (default: latest).", default=None)
    p.add_argument("--snapshot-mode", choices=["off", "light", "heavy"], default="heavy",
                   help="Accepted for compatibility; not used here.")
    args = p.parse_args()

    run_dir = _find_run_dir(args.run_id)
    diff_path = run_dir / "diff" / "report.json"
    if not diff_path.exists():
        raise RuntimeError(f"Diff report not found: {diff_path}")

    summary = json.loads(diff_path.read_text(encoding="utf-8"))
    changed = summary.get("tables_changed", [])

    # Dual logging
    src = __file__.replace("\\", "/")
    log_memory_event(
        event_text="db_snapshot_auditor report",
        source=src,
        tags=["tool", "snapshot", "audit"],
        content={"run_dir": run_dir.as_posix(), "tables_changed": changed},
        phase=REQUIRED_PHASE,
    )
    log_trace_event(
        description="db_snapshot_auditor report",
        source=src,
        tags=["tool", "snapshot", "audit"],
        content={"run_dir": run_dir.as_posix(), "tables_changed": changed},
        phase=REQUIRED_PHASE,
    )

    print(f"[auditor] run_dir={run_dir.as_posix()} tables_changed={len(changed)}")
    if changed:
        print("[auditor] changed tables:", ", ".join(changed))


if __name__ == "__main__":
    run_cli()

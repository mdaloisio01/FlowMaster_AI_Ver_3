# Path injection must be first
from boot.boot_path_initializer import inject_paths
inject_paths()

import sqlite3
from pathlib import Path

from core.sqlite_bootstrap import DB_PATH
from core.phase_control import REQUIRED_PHASE, ensure_phase
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event


REQUIRED_TABLES = {
    "boot_events",
    "memory_events",
    "trace_events",
    "manifest",
    "reflex_registry",
}


def run_cli() -> None:
    ensure_phase()

    log_memory_event(
        event_text="tests: db_integrity start",
        source=__name__,
        tags=["test", "start", "db"],
        content={"db": DB_PATH.as_posix()},
        phase=REQUIRED_PHASE,
    )

    assert DB_PATH.as_posix().startswith("root/"), f"DB must be under root/: {DB_PATH}"

    con = sqlite3.connect(DB_PATH.as_posix())
    try:
        names = {r[0] for r in con.execute("select name from sqlite_master where type='table'")}
    finally:
        con.close()

    missing = sorted(REQUIRED_TABLES - names)
    assert not missing, f"Missing tables: {missing}"

    log_trace_event(
        description="tests: db_integrity done",
        source=__name__,
        tags=["test", "done", "db"],
        content={"tables_found": sorted(names)},
        phase=REQUIRED_PHASE,
    )
    print("✅ db_integrity ok")


if __name__ == "__main__":
    run_cli()

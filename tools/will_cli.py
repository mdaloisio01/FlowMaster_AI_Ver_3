from __future__ import annotations
# tools/will_cli.py — Will CLI dispatcher (info-only phase, no enforcement)

import argparse
import importlib
import sys
from pathlib import Path

# Ensure repo root on sys.path
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# Paths + phase info (no enforcement)
from boot import boot_path_initializer as bpi
bpi.inject_paths()

from core.phase_control import get_current_phase, REQUIRED_PHASE  # REQUIRED_PHASE is informational now
from core.trace_logger import log_trace_event


def _call_run_cli(mod_path: str) -> int:
    """
    Import a module by dotted path and call its run_cli() if present.
    Returns 0 on success, non-zero otherwise.
    """
    try:
        mod = importlib.import_module(mod_path)
    except Exception as e:
        log_trace_event(
            "will_cli.import_error",
            {"module": mod_path, "error": repr(e)},
            source="tools.will_cli",
            phase=get_current_phase(),
        )
        return 2

    fn = getattr(mod, "run_cli", None)
    if callable(fn):
        try:
            fn()
            return 0
        except SystemExit as se:
            # Some run_cli() implementations call SystemExit
            code = int(se.code) if se.code is not None else 0
            return code
        except Exception as e:
            log_trace_event(
                "will_cli.run_cli_error",
                {"module": mod_path, "error": repr(e)},
                source="tools.will_cli",
                phase=get_current_phase(),
            )
            return 3
    else:
        log_trace_event(
            "will_cli.no_run_cli",
            {"module": mod_path},
            source="tools.will_cli",
            phase=get_current_phase(),
        )
        return 4


def run_cli() -> None:
    parser = argparse.ArgumentParser(
        prog="will",
        description=f"Will CLI dispatcher (Phase info: {get_current_phase()})"
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("ping", help="Run reflex_trace_ping")
    sub.add_parser("boot", help="Run boot loader")

    args = parser.parse_args()

    if args.command == "ping":
        rc = _call_run_cli("reflexes.reflex_core.reflex_trace_ping")
        log_trace_event(
            "will_cli.done",
            {"command": "ping", "rc": rc},
            source="tools.will_cli",
            phase=get_current_phase(),
        )
        raise SystemExit(rc)

    if args.command == "boot":
        rc = _call_run_cli("boot.boot_phase_loader")
        log_trace_event(
            "will_cli.done",
            {"command": "boot", "rc": rc},
            source="tools.will_cli",
            phase=get_current_phase(),
        )
        raise SystemExit(rc)

    # No command provided → print help
    parser.print_help()
    log_trace_event(
        "will_cli.done",
        {"command": None, "rc": 0},
        source="tools.will_cli",
        phase=get_current_phase(),
    )
    raise SystemExit(0)


if __name__ == "__main__":
    run_cli()

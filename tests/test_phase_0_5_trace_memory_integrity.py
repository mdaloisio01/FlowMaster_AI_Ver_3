# tests/test_phase_0_5_trace_memory_integrity.py
# Ensures snapshot wrapper dual-logs and memory↔trace cross-check passes.

from boot.boot_path_initializer import inject_paths
inject_paths()

import sys

from core.phase_control import ensure_phase


def _run_wrapper(module: str | None):
    import tools.trace_memory_snapshot as wrapper

    argv_backup = sys.argv[:]
    if module:
        sys.argv = ["trace_memory_snapshot.py", "--module", module, "--snapshot-mode", "heavy"]
    else:
        sys.argv = ["trace_memory_snapshot.py", "--snapshot-mode", "heavy"]
    try:
        wrapper.run_cli()
    finally:
        sys.argv = argv_backup


def test_crosscheck_clean_on_ping():
    ensure_phase()

    # Run the known reflex (dual logs)
    _run_wrapper("reflexes.reflex_core.reflex_trace_ping")

    # Import and run the cross-checker programmatically
    import tools.trace_memory_crosscheck as xcheck
    result = xcheck.audit(run_id=None, window=500)  # look at recent events

    # There should be no unmatched snapshot start/done between memory and trace
    assert not result["memory_only_starts"], f"Unmatched memory starts: {result['memory_only_starts']}"
    assert not result["trace_only_starts"], f"Unmatched trace starts: {result['trace_only_starts']}"
    assert not result["memory_only_dones"], f"Unmatched memory dones: {result['memory_only_dones']}"
    assert not result["trace_only_dones"], f"Unmatched trace dones: {result['trace_only_dones']}"

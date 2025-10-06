# Dev Bot Load File — v2 (Soft Phase Guard Compliant)

**Goal:** Make builds reliable and fast by removing hard, import-time phase enforcement.
Phase posture is **soft/warn by default**; flip to **strict/fail** in CI or when explicitly enabled.

This file defines how entrypoint CLIs (and servers) load, guard, and log — in line with the **Soft Phase Guard**.

---

## Core Principles

* **No import-time enforcement.**
  Import-time checks create circular imports and can collide with `from __future__` placement rules. Keep libraries importable; enforce **only at entrypoints** (CLIs/servers).

* **Single source of truth (manifest).**
  Use `core.phase_control.get_current_phase()` which reads **configs/ironroot_manifest_data.json → current_phase** (manifest only).

  * To diagnose/debug, you MAY set `WILL_PHASE_OVERRIDE` — this does **not** change the manifest; it is logged and surfaced in reports.

* **Soft by default, strict in CI/seal.**
  `ensure_phase(required)` **warns** and continues locally.
  If `WILL_PHASE_STRICT=1` (or CI detected), the same call **raises** and fails fast with a JSON report.

* **Structured, append-only logs.**
  Write JSON Lines (one JSON object per line) to `logs/` for trace and memory. Logs are audit-grade and referenced by sweep/reports.

---

## Required Load Sequence (for entrypoints)

1. **Inject paths**

   ```python
   from boot import boot_path_initializer as bpi
   bpi.inject_paths()
   ```

2. **Phase guard (entrypoints only)**

   ```python
   from core.phase_control import ensure_phase, REQUIRED_PHASE, get_current_phase

   # REQUIRED_PHASE is resolved from the manifest.
   # Soft posture by default; strict if WILL_PHASE_STRICT=1
   ensure_phase(REQUIRED_PHASE)
   ```

   * Libraries must NOT call `ensure_phase()`; keep them import-safe.
   * `get_current_phase()` returns manifest phase for display/logging.

3. **Logging API (stable)**

   ```python
   from core.trace_logger import log_trace_event, log_memory_event

   log_trace_event("tool.start", {"args": {...}}, source="tools.my_tool")
   # ... work ...
   log_trace_event("tool.done", {"rc": 0}, source="tools.my_tool")
   ```

   * Trace breadcrumbs → `logs/reflex_trace_log.jsonl`
   * Memory events → `logs/memory_log.jsonl`

---

## Do / Don’t

**Do**

* Call `ensure_phase()` **only** from entrypoints (`tools/*`, servers).
* Keep any `from __future__` lines at the very top (after an optional module docstring only).
* Log warnings/errors as JSONL; treat logs as the source of truth.
* Run the **Strict Phase Sweep** from CI/nightly to verify posture & manifest.

**Don’t**

* Don’t inject phase guards inside libraries (`core/*`, `boot/*`, `reflexes/*`).
* Don’t hard-code phase numbers in code; `REQUIRED_PHASE` comes from the manifest.
* Don’t rely on env to “set the phase” functionally; env override is **diagnostic**, not authoritative.

---

## Environment

* `WILL_PHASE_STRICT=1` — CI/seal mode: `ensure_phase()` raises on mismatch (fail-fast).
* `WILL_PHASE_OVERRIDE=<phase>` — **diagnostics only**: shows as an override in logs/reports; does **not** change manifest authority.

> Keep posture in **environment variables**, not code.

---

## File/Log Conventions

* **Trace log**: `logs/reflex_trace_log.jsonl` (append-only JSONL).
* **Memory log**: `logs/memory_log.jsonl` (append-only JSONL).
* **Phase guard sweep log**: `logs/phase_guard_log.jsonl` (strict sweep results).
* **Encoding**: UTF-8; one complete JSON object per line.
* **Paths in logs**: prefer forward slashes for portability.

---

## Example CLI skeleton

```python
from __future__ import annotations
"""Minimal entrypoint skeleton aligned with Soft Phase Guard."""

from boot import boot_path_initializer as bpi
bpi.inject_paths()

from core.phase_control import ensure_phase, REQUIRED_PHASE, get_current_phase
from core.trace_logger import log_trace_event

def run_cli() -> None:
    # Guard once at the entrypoint (soft by default; strict in CI via env)
    ensure_phase(REQUIRED_PHASE)

    log_trace_event("my_cli.start", {
        "phase_current": get_current_phase(),
        "args": {}
    }, source="tools.my_cli")

    # ... do work ...

    log_trace_event("my_cli.done", {"rc": 0}, source="tools.my_cli")

if __name__ == "__main__":
    run_cli()
```

---

## Strict Phase Sweep (nightly & on-demand)

* CLI: `tools/phase_guard_sweep.py`

  * Soft by default; `--strict` fails on mismatch and emits `sweep_report.json`.
  * Last run status is recorded in `logs/phase_guard_log.jsonl` (include `required/current/posture/status`).

---

## PowerShell tip (quick, multi-line Python)

Use a here-string piped to Python:

```powershell
@'
from core.phase_control import get_current_phase
print(get_current_phase())
'@ | python -
```

Here-strings preserve newlines and quotes—handy for embedded scripts/snippets.

---

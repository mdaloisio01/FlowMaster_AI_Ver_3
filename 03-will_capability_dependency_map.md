# Will — Capability ↔ Dependency Map (Soft Phase Guard–Aligned)

**Purpose:** Define what each capability/reflex **expects to already exist** (imports, files, utilities) *before* it’s planned or run. This is **phase‑neutral** guidance for planners and interrogators; enforcement remains **soft by default** and occurs **only at entrypoints** per Soft Phase Guard.

**Phase Awareness (per Soft Phase Guard):**

* **Authority:** `configs/ironroot_manifest_data.json → current_phase` (manifest is the source of truth).
  `configs/phase_history.json` is a **ledger only**.
* **Getter:** `core.phase_control.get_current_phase()` (for info/telemetry).
* **Guard (entrypoints only):** `core.phase_control.ensure_phase(REQUIRED_PHASE)` → **warn by default**, **raise only** when `WILL_PHASE_STRICT=1` (or CI detected).
* **Env:** `WILL_PHASE_STRICT=1` (strict posture). `WILL_PHASE_OVERRIDE` is diagnostic‑only (logged), **not** authoritative.

---

## Capability → Required Components (Phase 0–99+)

| Capability                       | Required Components                                                          | Min Phase | Posture    |
| -------------------------------- | ---------------------------------------------------------------------------- | --------- | ---------- |
| **Path injection**               | `boot.boot_path_initializer.inject_paths()`                                  | 0.1       | Neutral    |
| **Trace logging**                | `core.trace_logger.log_trace_event` → `logs/reflex_trace_log.jsonl` (JSONL)  | 0.1       | Neutral    |
| **Memory logging**               | `core.trace_logger.log_memory_event` → `logs/memory_log.jsonl` (JSONL)       | 0.1       | Neutral    |
| **Phase awareness (soft guard)** | `core.phase_control.get_current_phase`, `core.phase_control.ensure_phase`    | 0.7       | **Soft**   |
| **Boot seeding**                 | `boot.boot_phase_loader` (+ `root/first_boot.lock`)                          | 0.2       | Neutral    |
| **Reflex ping**                  | `reflexes.reflex_core.reflex_trace_ping`                                     | 0.2       | Neutral    |
| **Dev CLI**                      | `tools.will_cli` (`ping`, `boot`)                                            | 0.2       | Soft‑aware |
| **Manifest audit**               | `tools/manifest_*`, `configs/ironroot_manifest_data.json`                    | 0.3       | Neutral    |
| **DB snapshot audit**            | `tools/snapshot_db.py`, SQLite                                               | 0.5       | Neutral    |
| **Reflex compliance guard**      | `tools/reflex_compliance_guard.py`, canonical reflex template                | 0.4       | Neutral    |
| **Reflex coverage report**       | `tools/reflex_coverage_report.py` (scan entrypoints, logging presence)       | 0.7       | Neutral    |
| **Reflex self‑test runner**      | `reflexes/reflex_core/reflex_self_test_runner.py`, dual logging              | 0.7       | Neutral    |
| **Reflex router**                | `reflex_router.py`, manifest lookup, subreflex dispatcher                    | 1.0       | Soft‑aware |
| **Agent planner**                | `agent_planner.py`, memory tag filters, reflex metadata map                  | 2.0       | Soft‑aware |
| **Memory summary**               | `memory_summary.py`, memory fetch helpers, tag parser                        | 2.1       | Neutral    |
| **Macro execute chain**          | `macro_execute_chain.py`, `macro_reflex_map`, chain validator, stub handlers | 10.0      | Soft‑aware |
| **Trace/Memory cross‑check**     | `tools/trace_memory_crosscheck.py`, coverage scanner                         | 0.7       | Neutral    |
| **Snapshot index**               | `snapshot_index.json` (store CLI ↔ reflex coverage at phase seal)            | 8.0       | Neutral    |
| **Phase scheduler reflex**       | `phase_scheduler_reflex.py`, `schedule.yaml`, scheduler log schema           | 9.0       | Soft‑aware |

> **Soft‑aware** = entrypoints **may** call `ensure_phase()`; default is **warn+log**, strict failure only under `WILL_PHASE_STRICT=1`.

---

## GPT Rules of Engagement (for planners/interrogators)

* **Before** proposing or building any capability/reflex, verify that the **Required Components** above **exist and import cleanly**.
* If anything is missing/uncertain, **pause** and produce a **Dependency Interrogation Report** (no code) with recommended next steps (verify‑only or outline minimal prerequisites).
* Treat phase as **advisory** during dev: include phase info in logs; recommend strict mode only for CI/sealing.

---

## Notes & Conventions

* **No import‑time phase checks** inside libraries (`core/*`, `boot/*`, `reflexes/*`). Keep modules importable.
* **Structured logs:** JSON Lines in `logs/` (append‑only): `ts`, `event`, `data`, `source`, `phase`.
* **Env toggles:** `WILL_PHASE_STRICT=1` (strict posture). `WILL_PHASE_OVERRIDE` (diagnostic only; surfaced in reports).
* **Manifest is authoritative** for current phase; history is a ledger.

**End of File**

# 📘 Will Phase Capability Map (Soft‑Guard Edition, Updated)

**Purpose:** Define what each phase of Will is intended to unlock so builders (and bots) can reason about what’s appropriate **without** hard, import‑time blockers. This map is **phase‑neutral guidance** for planners/interrogators. Runtime enforcement remains **soft by default** and occurs **only at entrypoints** per Soft Phase Guard.

## Soft Phase Guard Alignment (Authority & Posture)

* **Authority for current phase:** `configs/ironroot_manifest_data.json → current_phase` (manifest is the source of truth).
  `configs/phase_history.json` is a **ledger only** (not authoritative).
* **Getter:** `core.phase_control.get_current_phase()` (use for display/telemetry and planning context).
* **Guard (entrypoints only):** `core.phase_control.ensure_phase(REQUIRED_PHASE)` → **warn & log by default**; **raise in CI** when `WILL_PHASE_STRICT=1`.
* **Env flags:**

  * `WILL_PHASE_STRICT=1` — enables strict posture (CI/seal).
  * `WILL_PHASE_OVERRIDE=<phase>` — **diagnostic only** (logged), does **not** change authority.

---

## 🧱 Phase Capability Table (0–99+)

| Phase | Codename                        | Capability Unlocked                                                         |
| ----: | ------------------------------- | --------------------------------------------------------------------------- |
|   0.0 | IronSpine Boot                  | Core folders, phase info helpers, `inject_paths()`                          |
|   0.1 | Logging Core                    | `log_trace_event()`, `log_memory_event()`, JSONL logs (`logs/`)             |
|   0.2 | DB Compliance                   | SQLite schema/health basics; test insert/fetch                              |
|   0.3 | Trace Pings                     | Basic trace reflex + CLI wire‑up (`reflex_trace_ping.py`)                   |
|   0.4 | Compliance Guard                | Canonical reflex template, `reflex_compliance_guard.py`                     |
|   0.5 | Reflex Memory Discipline        | Dual‑logging expectations across reflexes (trace + memory)                  |
|   0.6 | Trace Alignment                 | CLI ↔ reflex ↔ memory ↔ trace integrity checks                              |
|   0.7 | TraceSync & Reflex Audit        | Coverage report, self‑test runner, stub auditing                            |
|   0.8 | Reflex Router Init              | CLI reflex router with manifest/registry integration                        |
|   1.0 | Reflex Execution Core           | `reflex_router.py`, `reflex_executor.py`, WillClones stub points            |
|   1.1 | Persona Routing Engine          | Persona‑scoped dispatch, `persona_profiles.json`                            |
|   1.2 | Goal Chaining                   | Multi‑step reflex planning (`goal_planner.py`)                              |
|   2.0 | Agent Planner                   | Memory‑informed plan synthesis (`agent_planner.py`)                         |
|   2.1 | Memory Summary / Replay         | `memory_summary.py`, `memory_replay.py`                                     |
|   3.0 | GUI + Voice Hybrid Init         | GUI panels, FastAPI endpoints (when introduced), voice overlay              |
|   4.0 | Self‑Healing Reflexes           | `reflex_rebuilder.py`, repair from tests/stubs                              |
|   5.0 | WillClone Orchestration         | Fork/merge memory isolates; agent_pool                                      |
|   6.0 | Live WillCore Runtime           | Background loop, reflex event listener                                      |
|   7.0 | Memory Tag Lenses               | Cross‑phase memory lenses/filters                                           |
|   8.0 | Snapshot State Manager          | Snapshot/restore tools, JSON snapshots                                      |
|   9.0 | CLI/GUI Phase Scheduler         | Phase schedule & seal flow (policy‑level; runtime stays soft)               |
|  10.0 | Reflex Macro Engine             | Macro definition/runner (`macro_execute_chain`)                             |
| 11–20 | LLM Routing Layer               | `ask_gpt()`, `gpt_router.py`, tag‑based conditioning, local/global fallback |
| 21–30 | Multi‑Agent Council Layer       | Council voting, persona‑scoped agent groups, runtime role guards            |
|    31 | LLM_Brainstem (Local Models)    | Local model failover (e.g., GPTQ/Mistral), `local_llm_core.py`              |
|    32 | SnapApp GUI + Panel Filters     | Snapshot viewer, reflex test overlay, persona filters                       |
|    33 | Reflex Diagnostic Core          | `reflex_self_test_all()`, full audit (trace + memory + CLI)                 |
|    34 | Persona Tone Layer              | Tone filters (dev/support/analyst), bound to `persona_profiles.json`        |
|    35 | Plugin Interface + API Launcher | Plugin loader + triggers, `plugin_registry.json`                            |
| 36–98 | Evolution + Meta‑Agent Engine   | Long‑horizon learning, mesh, Will↔Will communication                        |
|    99 | Sovereign Funbox                | Humor, mirroring, travel helper, voice UI, etc.                             |

> **Note:** Phases communicate *intent & readiness*. They guide planning and CI policy, not runtime import behavior.

---

## 📌 GPT Behavior (Soft by Default)

* Always call `get_current_phase()` first to establish context.
* If a requested action sits in a **future phase**:

  * **Warn**: “This is Phase X; current is Phase Y.”
  * Offer a **staged plan** (what’s feasible now vs later).
  * Mention CI strictness: “Set `WILL_PHASE_STRICT=1` in CI to hard‑fail future‑phase execution.”
* Prefer **adapters/stubs** and **structured logs** over blocking; never add import‑time blockers in libraries.

---

## 🔧 Operational Notes

* **Entry‑point enforcement only**: CLIs/servers may call `ensure_phase(REQUIRED_PHASE)`; libraries must remain import‑safe.
* **Logs**: Use JSONL (`logs/reflex_trace_log.jsonl`, `logs/memory_log.jsonl`) for audit‑grade traces.
* **Env recap**: `WILL_PHASE_STRICT=1` (strict posture), `WILL_PHASE_OVERRIDE` (diagnostic only).
* **Manifest is authoritative**; history is a ledger for audits.

**End of File**

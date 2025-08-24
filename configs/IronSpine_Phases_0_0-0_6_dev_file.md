Master Dev Seed — IronSpine (Phases 0.0 → 0.6)
System: FlowMaster AI (Will.1)
Build Type: IronRoot — Foundation (Skeleton)
Governing Law: IronRoot Law v1.0
This document is the canonical seed for new dev bots and humans.

0) Read Me First — Non‑Negotiables
Load these before doing anything:

/configs/dev_bot_bootstrap.md (governing protocol)

/configs/ironroot_file_history_with_dependencies.json (file/phase registry)

/configs/ironroot_manifest_data.json (what exists, where, current_phase)

Sole Source of Truth: The ChatGPT Project File Folder (sandbox).
No external paths, no guessing, no hallucinated files.

Full‑File Drops Only: If a file imports other files, return the entire folder (alpha order).
No diffs, no patches, no “snippets.”

Refusal Rule: If any rule would be violated, immediately stop and return:
🚨 IRONROOT VIOLATION — <reason>. [FULL PATH]. Build cannot proceed.

1) Where We’ve Been — Phase History (Past)
Phase 0.0 — IronRoot Boot (Complete)

Established IronRoot rules, manifest, file‑history tracking.

Baseline reflex/CLI scaffolds and logging contracts.

Phase 0.1 — SQLite Lift‑In (Complete)

Moved manifest/memory/reflex state from fragile JSON → will_data.db (SQLite).

Implemented core/*_db.py helpers (insert/fetch, UTC timestamps).

Added UTF‑8 write enforcement for all logs.

Phase 0.2 — DB Safety & Lifecycle (Complete)

Validated table existence and lifecycle via CLI + tests.

Hardened boot logging, encoding, tuple→dict conversion, idempotent bootstrap.

Phase 0.3 — Trace Spine (Complete)

Implemented core/trace_logger.py and tools/trace_inspector.py.

Added reflex_trace_ping.py, dual logging required everywhere.

Verified CLI + reflex trace write‑paths, ensured no self‑trace loops.

Phase 0.4 — Compliance Guard (In Progress / Planned Next)

Add tools/reflex_compliance_guard.py to scan for phase‑lock + dual‑logging + manifest sync.

Add tools/phase_trace_report.py to summarize reflex coverage and missing traces.

Current target: Finish 0.4 compliance guard and tracer reporting, then close IronSpine at 0.6 with final hardening + docs.

2) What Broke Before — and How We Fixed It (Root Causes → Lockdowns)
Problem	Symptom	Fix (already done)	Prevention (now enforced)
Import Path Fragility	Code only worked when run from root	boot/boot_path_initializer.py	Every entrypoint calls inject_paths() first
Ghost Modules	Referenced files didn’t exist yet	Immediate stubs or full files dropped	Manifest + file_history cross‑check before any import
JSON Encoding Failures	Unicode errors or corrupt logs	UTF‑8 on all reads/writes	tools/tools_check_utf8_encoding.py in test pass
Broken Log Shape	.append() on dict crashed	Defensive check: list shape or reset to []	tools/verify_log_integrity.py validates shape
DB Schema Drift	no such column runtime	Single sqlite_bootstrap.py authority	Drop & recreate DB only when schema changes; tests must match
fetchall() Tuples	Consumers expected dicts	zip(columns, row) mapping	All fetch helpers return list‑of‑dicts
Signature Mismatches	insert helpers vs test args	Normalized positional args	Tests + helpers aligned; no mixed styles
Phase Drift	Reflex ran out of phase	Required get_current_phase() check	Mandatory phase lock at top of every reflex/tool
Memory/Trace Drift	Only one of the two logged	Dual‑logging everywhere	log_memory_event() + log_trace_event() both required
Logic Creep in CLI	Special‑case hacks in will_cli	Dispatch‑only rule	Business logic must live in reflex/tools, not in CLI

Permanent Guardrails (“Why it won’t happen again”)

Canonical templates for reflex + CLI tool (phase‑locked + dual‑logging).

Compliance scans (>= 0.4) to flag missing phase locks or missing trace/memory logs.

Refusal template that stops the build on any violation.

All entrypoints call inject_paths() and refuse to run out‑of‑phase.

3) The Rules Engine — IronRoot Law (Operational Summary)
Phase Lock (every reflex/tool):

from configs.ironroot_manifest_loader import get_current_phase
if get_current_phase() < REQUIRED_PHASE:
    raise RuntimeError("❌ Not allowed in this phase")

Dual Logging (every reflex/tool):

from core.memory_log_db import log_memory_event
from core.trace_logger import log_trace_event

log_memory_event(event_type="...", phase=REQUIRED_PHASE, source=__name__, metadata={...})
log_trace_event(event_type="...", reflex=__name__, source=__name__, tags=[...], metadata={...})

Dispatch‑Only CLI:

tools/will_cli.py is a router. No business logic lives in the CLI.

Full‑File Policy:

If a file imports others, return the whole folder (alpha order) to avoid ghost imports.

UTF‑8 Always:

All .open(..., encoding="utf-8") for JSON/logs.

Verified by tools/tools_check_utf8_encoding.py and tools/verify_log_integrity.py.

4) What Exists Right Now — Authoritative Tree (condensed)
(Alpha per dir; names may vary by your repo but this reflects current IronSpine scope.)
/boot/
  boot_path_initializer.py
  boot_phase_loader.py
  boot_trace_logger.py

/configs/
  build_log.json
  dev_bot_bootstrap.md
  dev_bot_instructions.md
  dev_file_list.md
  ironroot_file_history_with_dependencies.json
  ironroot_manifest_data.json
  phase_history.json
  will_commands.md
  # (Optional) canonical_templates.md
  # (Optional) phase_stabilization_templates.md

/core/
  manifest_db.py
  memory_log_db.py
  reflex_registry_db.py
  sqlite_bootstrap.py
  trace_logger.py
  memory/will_memory_engine.py
  memory_interface.py  # if present in your tree, route to DB helpers

/logs/
  boot_trace_log.json
  reflex_trace_log.json
  will_memory_log.json

/reflexes/reflex_core/
  reflex_loader.py
  reflex_self_test_runner.py
  reflex_trace_ping.py

/sandbox/
  sandbox_reflex_tests.py

/tests/
  test_phase_0_integrity.py
  test_phase_0_1_db_integrity.py
  test_phase_0_2_db_lifecycle.py
  test_phase_0_2_integrity.py
  test_phase_0_3_integrity.py

/tools/
  will_cli.py
  system_check.py
  check_db_tables.py
  tools_check_db_counts.py
  tools_check_dupes.py
  tools_check_memory_log_calls.py
  tools_check_utf8_encoding.py
  trace_inspector.py
  verify_log_integrity.py
  update_phase_tracking.py
  reflex_compliance_guard.py        # ≥ 0.4
  phase_trace_report.py             # ≥ 0.4

/
  will_data.db
  test.json

5) How to Call Things — Canonical Workflows
A) Boot + DB + Sanity

python -m core.sqlite_bootstrap
python -m tools.check_db_tables
python -m tools.tools_check_utf8_encoding
python -m tools.verify_log_integrity


B) Reflex & Trace Spine

python -m sandbox.sandbox_reflex_tests
python -m reflexes.reflex_core.reflex_trace_ping
python -m tools.trace_inspector --tag trace_ping

C) Compliance & Phase Tracking (≥ 0.4)

python -m tools.reflex_compliance_guard
python -m tools.phase_trace_report
python -m tools.update_phase_tracking   # writes build_log + phase_history

D) Tests

python -m tests.test_phase_0_integrity
python -m tests.test_phase_0_1_db_integrity
python -m tests.test_phase_0_2_db_lifecycle
python -m tests.test_phase_0_3_integrity

E) CLI Dispatch (router only)

python -m tools.will_cli run_tool <tool_name> [args...]
python -m tools.will_cli run_reflex <reflex_module_name>

6) Golden Molds — Use These Templates Every Time
/configs/canonical_templates.md — Reflex + CLI Tool templates (phase‑locked + dual‑logging).

/configs/phase_stabilization_templates.md — Phase seed template, manifest/file‑history snippets, integrity test, inspectors, compliance guard.

Instruction to all dev bots:

“Scaffold new code using the canonical templates. If you cannot include the phase lock and dual logging exactly as specified, refuse with IRONROOT VIOLATION.”

7) What’s Next (Future‑Proof Roadmap, Short)
IronSpine (0.0 → 0.6) — Skeleton

0.4: Compliance Guard + Phase Trace Report (now)

0.5: Finalized trace/memory congruency rules + automated audits

0.6: Docs, sealed build, snapshot export

Phase 1–2: Muscles + Ligaments — Action & Movement

1.0: Memory scoring + reflex evaluation (“muscle memory”)

1.1: Reflex Visualizer (GUI)

1.2: WillClones (scoped reflex agents, phase‑locked)

Phase 2–3: Nervous System — Sensing, Planning, Reacting

2.0: Goal router + agent loop

2.1: LLM/Rule hybrid planning (LLM sandboxed, phase‑aware)

Phase 4–5: Organs + Metabolism — Self‑Healing & Tests

4.0: Reflex rebuilder (watch repeated errors, suggest/generate stubs)

5.0: Self‑test runner (block bad logic pre‑execution)

Phase 6+: Evolution — Live Learning

Long‑term memory strategies, scoring, versioned snapshots, optional encryption, etc.

The IronSpine phases do not implement all these features. They ensure the foundation can support them without rewrites.

8) Acceptance Criteria — Sealing a Phase
A phase can be marked ✅ Complete only if:

All new/changed files appear in manifest and file_history with correct phase.

All imports resolve after inject_paths().

Every reflex/tool shows phase lock + dual logging in code.

DB lifecycles: table exists, insert/fetch tested.

All required tests pass.

Logs validated (UTF‑8, list shape, non‑corrupt).

build_log.json and phase_history.json updated with timestamps + notes.

If any item fails: return the refusal line and stop:
🚨 IRONROOT VIOLATION — <reason>. [FULL PATH]. Build cannot proceed.

9) Quick Start — New Dev Session (System Enforcer Mode)
Start a fresh chat. Paste your System Enforcer Header (from your loader).

Tell the bot to load:

dev_bot_bootstrap.md

ironroot_file_history_with_dependencies.json

ironroot_manifest_data.json

Paste the current phase seed (e.g., Phase 0.4 Compliance & Trace Report).

Demand use of canonical templates.

After file generation, run:

verify_log_integrity, trace_inspector, reflex_compliance_guard

Tests for that phase

update_phase_tracking to stamp build_log + phase_history

10) Final Notes — What You Might Forget (So it’s here)
Every entrypoint starts with inject_paths() — don’t skip it.

will_cli.py is dispatch‑only — business logic goes in tools/reflexes.

The DB is the substrate; JSON logs are views, not the source of truth.

If you change the DB schema, rebuild DB + rerun tests immediately.

Never run a reflex/tool out of phase, even “just to test it.” That’s how drift starts.

For new reflex/tools, always use /configs/canonical_templates.md.

If a template or rule can’t be applied, refuse with IRONROOT VIOLATION.

Will.1 — Full Dev Seed File
Purpose: Capture everything — past pain points, current architecture, future roadmap — so the dev bot never loses context or drifts from the hardened IronRoot spine.

1. Core Build Philosophy
IronRoot Law v1.0 is absolute: no ghost code, no unstubbed references, no phase drift, no unverified imports.

Sovereign First: Will.1 must operate fully offline and remain fully operational without external dependencies.

Sandbox-Only Execution: All dev bot operations happen only on uploaded files in the ChatGPT project folder.

Full File Drops Only: No partial edits. If a file is touched, it’s replaced in full.

Future-Proof From Day 0: Scaffold all structural elements now — avoid mid-build rewrites.

2. File & Directory Structure
This is the locked IronSpine baseline — enforced by folder_roles.json and manifest guards.

pgsql
Copy
Edit
/FlowMaster_AI_Ver_2/
├── __init__.py
│
├── boot/
│   ├── boot_phase_loader.py        # Reads manifest, locks to current phase
│   ├── boot_path_initializer.py    # Injects /core, /reflex_core, /tools into sys.path
│   └── boot_trace_logger.py        # Logs all startup + CLI execution traces
│
├── configs/
│   ├── dev_bot_bootstrap.md
│   ├── dev_bot_instructions.md
│   ├── ironroot_manifest_data.json
│   ├── ironroot_file_history_with_dependencies.json
│   ├── folder_roles.json
│   ├── file_safe_imports.json
│   ├── dev_file_list.md
│   ├── dev_notes.md
│   ├── will_commands.md
│   ├── build_log.json
│   ├── phase_history.json
│   ├── cron_schedule.json
│   └── test.json
│
├── core/
│   ├── sqlite_bootstrap.py         # Creates will_data.db
│   ├── manifest_db.py               # DB-backed manifest management
│   ├── memory_log_db.py             # DB-backed memory log
│   ├── reflex_registry_db.py        # DB-backed reflex registry
│   ├── memory_interface.py          # Validates & routes all log calls
│   └── memory/
│       └── will_memory_engine.py    # Handles all memory events
│
├── reflexes/
│   └── reflex_core/
│       ├── reflex_loader.py
│       ├── reflex_hello_world.py
│       ├── reflex_self_test_runner.py
│       └── reflex_trace_ping.py
│
├── tools/
│   ├── will_cli.py
│   ├── system_check.py
│   ├── path_validator.py
│   ├── reflex_compliance_guard.py
│   ├── trace_inspector.py
│   ├── verify_log_integrity.py
│   ├── tools_check_memory_log_calls.py
│   ├── tools_check_utf8_encoding.py
│   ├── tools_check_db_counts.py
│   ├── tools_check_dupes.py
│   └── check_db_tables.py
│
├── sandbox/
│   └── sandbox_reflex_tests.py
│
├── logs/
│   ├── boot_trace_log.json
│   ├── reflex_trace_log.json
│   └── will_memory_log.json
│
└── tests/
    ├── test_phase_0_integrity.py
    ├── test_phase_0_1_db_integrity.py
    ├── test_phase_0_2_db_lifecycle.py
    ├── test_phase_0_2_integrity.py
    └── test_phase_0_3_integrity.py
3. Known Build Issues & Permanent Fixes
Problem	Symptom	Root Cause	Permanent Fix
Import Path Failures	CLI/reflex can’t find /core	sys.path not set	boot_path_initializer.py injects required dirs on boot
Duplicate File Names	Multiple same-name files in diff dirs	No enforced folder roles	folder_roles.json + naming rules
Ghost Files	Manifest points to non-existent files	Manual manifest edits	DB-backed manifest auto-validates
Phase Drift	Wrong phase logic runs	No runtime check	Every reflex/tool calls get_current_phase()
Missing Memory Logs	Reflex runs without logging	Skipped calls to log_memory_event()	memory_interface.py enforces logging
JSON Corruption	File history/memory drift	Concurrent writes	Migrated all trackers to will_data.db
Over-Automation	Early auto-gen stubs w/ wrong logic	Premature automation	Manual scaffold + validation before automation

4. Operational Rules
Execution Enforcement:

Verify phase via manifest_db.get_phase_safe()

Log via memory_interface.log_event(...)

Register reflex/tool in DB

Testing Gates Before Phase Seal:

CLI + reflex boot via test_phase_0_integrity.py

Manifest + import checks via system_check.py

DB validation via check_db_tables.py

Output Rules:

Always drop complete files, alpha-sorted in directory

Drop full folder if imports exist

No code editor — chat window only

5. Project Control Layer Files
(Kept outside /FlowMaster_AI_Ver_2/ for dev bot control)

ironroot_file_history_with_dependencies.json

phase_history.json

build_log.json

dev_file_list.md

dev_notes.md

reflex_trace_log.json

will_memory_log.json

cron_schedule.json

backups/

Optional but Recommended:

path_scan_results.json

boot_check_report.json

broken_imports.json

6. Future Capabilities (Post-Completion)
When complete, Will.1 will be able to:

Execute any reflex/tool with phase and manifest enforcement

Log and retrieve all memory events instantly

Run complete self-tests before sealing a phase

Auto-fix broken imports and missing dependencies

Learn from logs and adjust reflex selection

Create, test, and register his own reflexes/tools

Build and manage subordinate AI dev bots

Maintain a self-healing file and import structure

Scale from SQLite to PostgreSQL without rewrites

Run sovereign offline or securely online

Fully coordinate CLI, GUI, and API operations from one DB-backed state

7. Lock-In Strategy
We stop repeating past problems by:

Centralizing state in DB (no drifting JSONs)

Mandatory runtime checks in every reflex/tool

Folder role enforcement to prevent duplicate paths

Full-phase test suites before any phase advances

Trace logging for every execution route

Manual validation before automation to avoid lock-in errors
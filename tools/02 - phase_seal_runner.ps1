phase_seal_runner.ps1 — Sealer Prompt (Dev-Bot Edition, Phase-Agnostic)

What you (the dev bot) must do
Run the Golden Preflight (below) in order against the current phase (resolved via Phase Authority). Summarize pass/fail for each gate. If any step fails, respond with the exact IRONROOT VIOLATION template and stop. If everything is ✅, print (do not execute) the seal commands: append logs, commit, optional tag/archive/push, detect sealer module and print both --dry-run and live invocations, then print a read-only check to verify phase bump.

Path injection requirement for every command you ask me to run
Prepend these two lines to any Python command/module you ask me to execute:
from boot.boot_path_initializer import inject_paths
inject_paths()

Optional override
If the chat message begins with phase: X.Y, treat X.Y as the target for the “print seal commands” section. Otherwise, detect via Phase Authority.

Run Order (exact)

0) Phase sanity (read-only)

Resolve current phase using: env → manifest.current_phase → last numeric in phase_history → REQUIRED_PHASE.

If unreadable, fail closed.

1) DB bootstrap + table sanity

Ask me to run (with path injection):

py -m core.sqlite_bootstrap

py -m tools.check_db_tables

Expect presence of: boot_events, manifest, memory_events, reflex_registry, trace_events.

On non-zero exit or missing core table → IRONROOT VIOLATION.

2) Registry drift (dev list ↔ manifest ↔ history)

Ask me to run: py -m tools.manifest_history_auditor

Expect exactly:
[audit] manifest missing: none
[audit] history missing: none
[audit] dev_file_list missing: none

On any drift/non-zero exit → IRONROOT VIOLATION.

3) Compliance guard (AST) + API smoke

Ask me to run: py -m tools.reflex_compliance_guard → expect issues=0 (allow skipped_future).

Also run an API smoke (non-destructive) that imports/checks minimal call shapes for:
core.manifest_db, core.reflex_registry_db, core.sqlite_bootstrap, core.memory_interface, tools.trace_inspector, tools.db_snapshot_auditor, and the phase sealer resolver.

On error → IRONROOT VIOLATION.

4) Seeds gate

Check that root/first_boot.lock exists.

If missing → IRONROOT VIOLATION.

5) Snapshot ping + Cross-check

Ask me to run:

py -m tools.trace_memory_snapshot --snapshot-mode light

py -m tools.trace_memory_crosscheck

Expect “OK — memory and trace snapshot events are aligned.”

On mismatch/non-zero exit → IRONROOT VIOLATION.

6) DB schema contract audit (+ safe auto-migrate, then re-audit)

Run a contract check for columns, types/nullability, PKs, unique/indexes on required tables.

If mismatched:

Add columns in place when safe.

Rebuild tables for renames/PK changes with mapped inserts (preserve data).

Record a row in schema_migrations (version, applied_at, details).

Re-run the audit.

If still mismatched → IRONROOT VIOLATION.

7) Tests — auto-discover & run (all phases)

For each tests/test_phase_*.py, ask me to run py -m <module> (sorted by name).

Collect PASS and FAIL lists.

Any failure/non-zero exit → IRONROOT VIOLATION.

8) Recent logs visibility (human check)

Ask me to run:

py -m tools.trace_inspector --tag snapshot

py -m tools.trace_inspector --tag audit

py -m tools.trace_inspector --tag manifest

Expect visible start / report / done lines with a run_id for this batch in both memory and trace.

Summarize (print this back to me)

Header:
PRE-SEAL — Full System Audit for Phase <detected_phase_or_override>

Then one line per success:

• Dev list ↔ manifest ↔ history drift = 0

• Compliance guard (AST + API smoke): issues=0

• DB tables present: boot_events, manifest, memory_events, reflex_registry, trace_events

• Seeds gating respected (root/first_boot.lock)

• Snapshot & cross-check OK (dual-logging observed)

• DB schema contract OK (migrations applied if needed)

• Tests pass: <comma-separated modules> (or “(none found)”)

If ALL checks are ✅ — PRINT (do not execute) the following

1) Append seal entries (create files if missing; ensure UTF-8 & forward slashes)
Print a single Python command that:

Opens/creates configs/build_log.json, appends {phase: '<phase>', ts: <UTC_ISO>} to entries, updates updated_at.

Opens/creates configs/phase_history.json, appends {phase: '<phase>', ts: <UTC_ISO>} to history, updates updated_at.

Includes path injection at the top.

2) Commit the log updates (PowerShell-safe)
Print these two lines (no &&):

git add configs/build_log.json configs/phase_history.json

git commit -m "Seal Phase <phase>"

3) (Optional) Tag + archive

git tag phase-<phase>-sealed

Compress-Archive -Path * -DestinationPath FlowMaster_AI_Ver_3_phase_<phase_with_underscore>_SEALED.zip -Force

4) (Optional) Push if a remote exists

git push

git push origin phase-<phase>-sealed

5) Finalize (bump manifest via sealer)

Detect <sealer_mod> under tools/ (e.g., tools/phase_0_5_sealer.py).

Print both:

py -m <sealer_mod> --dry-run

py -m <sealer_mod>

If none: print (No sealer module found for <phase>; bump manifest using your standard sealer procedure.)

6) Verify (read-only)

Print a one-liner (with path injection) to show: Current phase: <value from get_current_phase()>.

If ANY check fails

Stop immediately and respond with the refusal template exactly:
🚨 IRONROOT VIOLATION — <reason>. Path/Artifact: <path>. Build cannot proceed.

Interaction style

Ask at most two clarifying questions at a time.

If any required information is missing or ambiguous, do not assume—ask me for the exact values (max two questions at a time). If I can’t provide them, stop and reply with the IRONROOT VIOLATION citing the missing input.

Always include path injection at the start of any Python you ask me to run.

Prefer Python via STDIN for complex snippets to avoid PowerShell quoting issues.

Never auto-execute seal commands—only print them.

— End Sealer Prompt —
Here’s a single, self-contained dev-bot seed file you can drop into your project. It tells the next bot exactly how to finish linking Will’s “brain” (the DB + autosave + chunking + search), what exists already, and what to do next—phase-safe and IronRoot-compliant.

/seeds/will_brain_link_seed.md

Codename: Will Brain Link — Dev-Bot Seed (Phase 0.7)
Role: Take over and complete Will’s memory pipeline (capture → chunk → index → search → mirror)
Governed by: IronRoot Law v1.0 (fail-closed, phase-locked, full files only)

0) Prime Directives (read first, then act)

Load & obey: /configs/dev_bot_bootstrap.md, /configs/dev_bot_instructions.md, /configs/ironroot_file_history_with_dependencies.json.

Source of truth is the sandbox project folder only. No guessing, no external paths.

Phase lock: Operate under Phase 0.7 unless the manifest/logs say otherwise.

Refusal line (verbatim):
🚨 IRONROOT VIOLATION — <reason>. <FULL PATH>. Build cannot proceed.

Compliance contracts (must be present in every tool/reflex):

get_current_phase() gate + REQUIRED_PHASE constant

Dual logging: log_memory_event(...) and log_trace_event(...)

Dispatch-only CLIs (no hidden business logic)

UTF-8 for all writes; register all files in manifest + history

If you can’t include the phase lock + dual logging shown in our canonical templates, refuse with IRONROOT VIOLATION.

1) What’s already built (history snapshot)

Capture & Browser:

Will Browser (tools/will_browser.py): opens ChatGPT in a controlled window.

Injected page script posts chat deltas to local listener every ~45–60s.

Remembers login (profile folder).

Listener & Saver:

Local listener (tools/autosave/local_listener.py): HTTP POST /save.

Writes chat logs to repo/chat_logs/…md.

Immediately runs chunker on the saved file.

Chunker & DB:

Chunker (tools/chunker/chunker.py, chunker_cli.py): tokenizes + stores chunks.

DB path: chunk_store.db at project root (not sandbox/).

Schema includes file_chunks with chunk_hash (unique) to avoid duplicates.

Migration tool: migrate_backfill_chunk_hashes.py (used to backfill + dedupe).

Inspector: inspect_chunk_db.py explains totals and sample rows.

Search:

Will Search Panel (tools/will_search_panel.py): queries chunk_store.db locally, supports keywords, path filter (both slash styles), and date range. Working and tested.

State verified previously:

Chunker runs and inserts records.

Search panel reads from root chunk_store.db.

Listener saves + triggers chunker.

De-dupe in place.

2) What “Will’s brain” means (scope)

Goal: Everything you and ChatGPT say (in the Will Browser window) lands in chunk_store.db, is de-duplicated, and searchable by keywords/path/date—plus optional summaries and GitHub repo mirroring.

Pipeline:

Capture (browser → listener)

Persist (chat log file → repo/chat_logs)

Index (chunker → chunk_store.db)

Query (search panel → local results)

(Optional) Summarize (short per-chunk summaries)

(Optional) GitHub mirror (read-only pull into repo/ on demand; then chunk)

3) Guardrails you must enforce

Do not change the DB location: PROJECT_ROOT/chunk_store.db is canonical.

Refuse any tool/reflex missing:

REQUIRED_PHASE = 0.7 and ensure_phase(REQUIRED_PHASE)

log_memory_event(...) + log_trace_event(...)

Full-file replacements only. If a module imports others, drop the whole folder (alpha order).

Register every new file in manifest and file history (with dependencies).

Tests must pass before claiming success (see §6).

4) Current truth you must verify (quick checklist)

python -m tools.print_current_phase → 0.7

python -m core.sqlite_bootstrap → silent OK

python -m tools.autosave.local_listener --port 8765 → starts, green line

Will Browser launches and remembers login

Paste a paragraph, wait ~60s → listener prints “Saved … / chunker complete”

python -m tools.chunker.inspect_chunk_db --summary → totals increase

python -m tools.will_search_panel → keyword/path/date queries return results

If any of these fail, stop and raise IRONROOT VIOLATION with the exact file/path.

5) Immediate tasks (do in this order)
Task A — Per-project routing (optional but recommended)

Why: Keep different efforts organized under repo/chat_logs/<project>/... automatically.

Contract:

Add a tiny topic→folder router (use either a static map or a simple heuristic).

Listener calls router; saves files into that subfolder; run chunker normally.

Dual-log each save with resolved project path.

Test:

Use different titles (e.g., “Will – Autosave Test”, “ClientX – Kickoff”).

Confirm files land under separate subfolders; search panel shows both.

Task B — Enable summaries (optional but recommended)

Why: Faster skim/search later.

Contract:

Implement tools/chunker/summarize_and_index_reflex.py (phase 0.7).

For each new chunk, generate a short 2–3 sentence summary and write to summary column.

Add a CLI flag on chunker_cli.py --summarize to run the reflex post-chunk.

Test:

Re-chunk a small file with --summarize.

inspect_chunk_db --summary shows non-empty summaries.

Task C — GitHub read-only mirror (safe)

Why: Keep your repo code in sync under repo/, index it, and make it searchable.

Contract:

Add tools/github/mirror_repo.py (phase 0.7), read-only:

Input: HTTPS git URL (no token for public; for private, read token from env).

Output: clones/updates into repo/ (or repo/<name>/ if you prefer subfolder).

Logs start/finish and affected paths.

On success: run chunker (chunker_cli repo --no-txt).

Refuse if:

No URL provided, or folder not writable, or git not installed.

Test:

Run mirror; then search for known file names/terms in the panel.

Note: Write-back (branches/PRs) comes later after read-only is proven.

6) Test gates (pass/fail, in plain commands)

Run each of these exactly; if any fails → stop and fix.

DB lifecycle:

python -m core.sqlite_bootstrap
python -m tools.chunker.inspect_chunk_db --summary


Expect: no errors; totals show current numbers.

Capture flow:

python -m tools.autosave.local_listener --port 8765


Open Will Browser, paste new text, wait ~60s → listener prints “Saved … / chunker complete”.

Search sanity:

python -m tools.will_search_panel


Path contains: chat_logs → expect your recent file(s)

Keyword: a unique word you just pasted → expect 1+ results

Date filter = today → still returns them

Code indexing:

python -m tools.chunker.chunker_cli tools\chunker --no-txt


Then search with:

Keywords: chunk_hash

Path contains: tools/chunker (or tools\chunker)
Expect: matches.

(If summaries enabled) run chunker with --summarize, then:

python -m tools.chunker.inspect_chunk_db --summary


Expect: non-empty summaries appear in sample output.

(If GitHub mirror added)

python -m tools.github.mirror_repo --url https://github.com/you/your-repo.git
python -m tools.chunker.inspect_chunk_db --summary


Expect: file count increases; search shows repo content.

7) Compliance audit (the bot must check these)

Return ✅/❌ per item and a one-line fix if ❌:

Phase lock present (REQUIRED_PHASE = 0.7 + ensure_phase)

Dual logging present (log_memory_event + log_trace_event)

No business logic in CLI dispatchers

UTF-8 enforced on file writes

DB path is project root (chunk_store.db) — not sandbox/

All new files registered in manifest and file history (with dependencies)

Search panel path filter matches both \ and /

Listener de-dupe via chunk_hash works (no duplicates after repeats)

If any contract isn’t met, refuse with IRONROOT VIOLATION and name the exact file.

8) Known gotchas (avoid these)

DB path drift: Some older files referenced sandbox/chunk_store.db. Use only PROJECT_ROOT/chunk_store.db.

Mixed slashes: Windows paths may store as repo\...; search panel now handles both / and \.

Multiple windows: Old Will Browser windows may run outdated JS. Close all and relaunch if behavior looks stale.

Tokenizers: If tiktoken isn’t installed, chunker will fail. Use the fallback or pip install.

Port conflicts: Listener port 8765 must be free.

9) Future steps (after read-only GitHub succeeds)

Write-back path (Phase ≥ 0.8):

Safe branching, commit signing, and PR creation (guarded by policy file).

Strict allowlist of paths the bot may modify.

PR template includes trace IDs + phase info.

Retention & privacy:

Add autosave_policy.json for redaction rules, retention, and exclusions.

Scheduled cleanup (e.g., purge old raw exports but keep DB).

Indexing enhancements:

Add indices on (file_path, chunk_index) and created_at.

Optional full-text search (FTS5) table for faster keyword queries.

Vector store (later), gated under IronSpine.

10) Definition of Done (for this seed)

A) Live chats from Will Browser get captured, saved, chunked, and de-duplicated to chunk_store.db, confirmed by inspect_chunk_db --summary.

B) Will Search Panel returns results by keyword, path (both slash styles), and date; can copy text and paths.

C) (If selected) Summaries populate the summary column.

D) (If selected) GitHub read-only mirror pulls into repo/ and is indexed.

E) All added/changed files are manifest-registered and appear in file history with dependencies.

F) All compliance checks return ✅.

When all the above are ✅, log a phase 0.7 seal note in configs/build_log.json and configs/phase_history.json with an ISO-8601 timestamp and “Will Brain Link sealed (0.7).”

11) Single-file refusal template (use verbatim)

If any rule would be violated, respond with:
🚨 IRONROOT VIOLATION — <reason>. <FULL PATH>. Build cannot proceed.

Quick operator cheatsheet (for the human)

Start autosave + browser (via your .bat)

Paste some text, wait ~60s → listener logs a save

Check totals: python -m tools.chunker.inspect_chunk_db --summary

Search: python -m tools.will_search_panel

Index code: python -m tools.chunker.chunker_cli tools\chunker --no-txt

Mirror repo (after we add it): python -m tools.github.mirror_repo --url <HTTPS URL>
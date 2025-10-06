# Dev Seed — Phase 0.7 Wrap, Git Hygiene, and 0.8 Prep

**Owner:** Mark
**Repo Root:** `FlowMaster_AI/FlowMaster_AI_Ver_3`
**Date/Time (UTC):** <!-- fill when run -->
**Seed Purpose:** Document what we did, the issues we hit, and the plan to keep IronRoot (IR)‑compliant while preparing for Phase 0.8. This seed can be ingested by a swarm/dev‑bot to replay or continue the work.

---

## Executive Summary

We finalized and sealed **Phase 0.7**, removed hard runtime phase enforcement (migrated to a soft guard/logging posture), verified trace/memory logging, and unblocked artifact emission. We also configured GitHub SSH and pushed a signed **tag `v0.7.0-sealed`**. The main outstanding area is **Git hygiene** (local changes and stashes) and ensuring a clean branch for **Phase 0.8** without accidentally mixing experimental files.

---

## What We Did (Chronological Highlights)

1. **Phase enforcement simplification**

   * Removed hard-coded phase requirement checks from runtime (kept a soft/observable guard via logs).
   * Updated `core.trace_logger` signatures (no `source`/`details` kwargs breakage).
   * Tools adjusted to use `log_trace_event(event, data, ...)` shape.

2. **Sanity tests**

   * `tools/print_current_phase.py` → reports `0.7`.
   * `tools/phase_trace_report.py` → healthy counts; no runtime gate failures.
   * `tools/will_cli.py ping` and `boot` now log clean start/done events.

3. **Sealed Phase 0.7**

   * Used **`06 - phase_seal_runner.ps1`** (fixed script) to write:

     * `configs/ironroot_manifest_data.json` → `current_phase: 0.7`, `current_version: "0.7.0-sealed"`.
     * `phase_history.json` → appended sealed entry.
     * trace lines in `logs/reflex_trace_log.jsonl` for `phase.sealed`.
   * Committed changes and **tagged** `v0.7.0-sealed` (force‑updated tag once to final).

4. **GitHub SSH setup**

   * Generated **ed25519** key, added to GitHub, verified with `ssh -T git@github.com`.
   * Pushed **tag** and later pushed **branch** `phase-0.8-dev`.

5. **Artifact Emitter**

   * Implemented `tools/artifact_emitter.py` (IR-compliant CLI).
   * Clarified seed syntax: emits only from fenced blocks like `file:path`.
   * Created a working seed `05-artifact_emitter_seed.md` (at repo root) producing:

     * `artifacts/hello.txt`, `artifacts/README.md`, `artifacts/sample.json`.

6. **Branch/Working-Tree hygiene**

   * Created `phase-0.8-dev` then **clean branch** `phase-0.8-dev-clean`.
   * Stashed local changes twice (`stash@{1}`, `stash@{0}`), applied top stash onto clean branch to continue selectively.

---

## The Issues We Hit

* **Legacy hard phase checks** caused CLI/tool errors when using the modern soft guard + updated logger signatures.
* **`log_trace_event` and `log_memory_event` kwargs** mismatches (e.g., `source=` / `details=`) broke several tools.
* **Seed discovery confusion** for Artifact Emitter (path vs. seed syntax). Once seed lived at repo root and used proper code‑fence format, it worked.
* **Git working tree drift**: a large set of modified/untracked files made branch switching and clean commits painful.

---

## Root Causes (Short)

* Tight coupling to old **phase enforcement** API across many tools.
* Mixed conventions for **trace logging** parameters.
* Ambiguity about **seed locations** and **emitter syntax**.
* Long‑running local dev without frequent commit/PR cadence → drift and stash complexity.

---

## Decisions (IR‑Compliant)

1. **Soft Phase Guard only** at runtime; enforcement moves to tooling and audit scripts.
2. **Canonical logging shape**

   * `log_trace_event(event: str, data: dict | None = None, source: str | None = None, phase: float | None = None, extra: dict | None = None)`
   * `log_memory_event(event_type: str, detail: dict | None = None, meta: dict | None = None, source: str | None = None, phase: float | None = None)`
3. **Artifact Emitter** expects Markdown seed with `file: FILENAME` fences; all outputs land under `./artifacts` (tracked as needed).
4. **Git hygiene**: keep `master` clean, do work on feature branches, PR back. Use **one small change per commit**.

---

## Current State (Now)

* **Phase 0.7 sealed** and tagged remotely.
* **`phase-0.8-dev-clean`** exists and is current working branch.
* Artifact Emitter functioning (seed at repo root works).
* SSH to GitHub is healthy (passphrase‑protected key).

---

## What We’re Trying to Do Next

* Keep **master clean**; use PRs from `phase-0.8-dev-clean`.
* Ensure all tools and reflexes comply with new **trace logger** signatures.
* Define a **Phase 0.8 seed** (when ready) to drive swarm tasks without re‑introducing hard phase gates.

---

## Minimal Fix Plan (Actionable)

### A) Lock in logging API

* [ ] Grep repo for `log_trace_event(` usages; convert to canonical signature.
* [ ] Same for `log_memory_event(`.
* [ ] Re‑run `tools/phase_trace_report.py`.

### B) Artifact Emitter

* [ ] Keep `05-artifact_emitter_seed.md` at repo root.
* [ ] Maintain fenced blocks with explicit `file:` headers.
* [ ] Commit `artifacts/*` that are meant to be versioned; ignore the rest.

### C) Git hygiene

* [ ] Remain on `phase-0.8-dev-clean` for dev.
* [ ] Commit in small slices; open PRs to `master`.
* [ ] Avoid long‑lived untracked files; add `.gitignore` or commit artifacts intentionally.

### D) Phase 0.8 Prep (no start yet)

* [ ] Draft `seeds/phase_0_8_seed.md` when ready.
* [ ] Swarm plan references: PhasePlan.json + plan_lock.json already present.

---

## Known Good Commands (Reference)

```powershell
# 1) Ensure Python sees the repo root
$env:PYTHONPATH = "$PWD"

# 2) Sanity: current phase & traces
python tools\print_current_phase.py
python tools\phase_trace_report.py

# 3) Artifact Emitter (root seed)
python tools\artifact_emitter.py --seed ".\05-artifact_emitter_seed.md" --dry-run
python tools\artifact_emitter.py --seed ".\05-artifact_emitter_seed.md"

# 4) Will CLI
python tools\will_cli.py ping
python tools\will_cli.py boot
```

Git (safe set):

```powershell
git status
git add <files>
git commit -m "<message>"
git push -u origin phase-0.8-dev-clean
```

---

## Artifacts & Files (as of 0.7 seal)

* `configs/ironroot_manifest_data.json` — `current_phase: 0.7`, `current_version: "0.7.0-sealed"`.
* `phase_history.json` — appended sealed entry (note="Manual seal").
* `artifacts/Phaseplan.json`, `artifacts/plan_lock.json` — 0.8 planning.
* `artifacts/hello.txt`, `artifacts/README.md`, `artifacts/sample.json` — emitter smoke outputs.

---

## IR Compliance Notes

* **No hard gate** at runtime; verification in tools (auditors/guards with logs).
* **Trace**: structured JSON lines; clear `event`, optional `source`, `phase`.
* **Seeds**: deterministic, explicit file fences; reproducible artifact output.
* **Git**: PR-based merges; sealed tags for phase milestones.

---

## Risks & Mitigations

* *Risk:* Tool still using old logger kwargs → **Mitigation:** repo-wide grep & fix, run auditor.
* *Risk:* Seed drift → **Mitigation:** keep emitter seeds near root with explicit fences.
* *Risk:* Local drift → **Mitigation:** frequent small commits & PRs; keep `.gitignore` sharp.

---

## Rollback Plan

* To undo recent emitter outputs: `git restore --staged artifacts/* ; git checkout -- artifacts/*` (or delete and re‑emit).
* To revert logger changes: `git revert` the specific commits.
* To abandon local drift: use `git stash` (temporary) or hard reset to `origin/branch` (destructive).

---

## Appendix A — Sample Artifact Emitter Seed

Use this pattern (place at repo root):

````md
# Artifact Emitter Seed (Example)

Some context or prose can go here. Only fenced blocks with `file:` emit files.

```file: artifacts/hello.txt
Hello from the Artifact Emitter!
This file was generated at {{utc_now}}.
````

```file: artifacts/README.md
# Artifacts Folder

These files were emitted by `tools/artifact_emitter.py` using the seed `05-artifact_emitter_seed.md`.

- **hello.txt** — sanity check string with timestamp
- **sample.json** — a tiny JSON payload for plumbing tests

Re-run the emitter any time to refresh; it overwrites with current content.
```

```file: artifacts/sample.json
{
  "emitted_at": "{{utc_now}}",
  "source_seed": "05-artifact_emitter_seed.md",
  "status": "ok",
  "items": ["hello.txt", "README.md", "sample.json"]
}
```

```

---

## Appendix B — One-time SSH Checklist (done)
- `ssh-keygen -t ed25519 -C "<email>"` → save to default path.
- Add `id_ed25519.pub` to GitHub → Settings → SSH and GPG keys.
- Verify: `ssh -T git@github.com` → “successfully authenticated”.

---

## Ready for Bot
**Instruction to Dev Bot / Swarm:**
- Validate logging API conformance across tools.
- Confirm artifact emitter reproducibility using the example seed.
- Keep changes on `phase-0.8-dev-clean`; propose PRs against `master`.
- Do **not** start Phase 0.8 execution yet; only prepare scaffolding.

```

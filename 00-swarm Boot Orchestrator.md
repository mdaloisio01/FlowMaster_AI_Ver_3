<!-- =============================================================
00-SWARM BOOT ORCHESTRATOR (CHAT MODE, PHASE-NEUTRAL, SOFT-GUARD)
**LOCAL-ONLY EDITION — NO GIT / NO GITHUB**
This file is a SPEC for ChatGPT-only execution. It contains no code to run.
Any bot that has your project files can follow these steps deterministically.

BULLET & LANGUAGE RULES (AUTO-NORMALIZE)
- Accept either "-" or "*" as bullets; normalize to "- ".
- Non-executable prose only: prefer "expected to / intended to".
- Never require import-time phase checks; entrypoints-only enforcement policy.

FILENAME TOLERANCE & PATH CANONICALIZATION
- Manifest: prefer configs/ironroot_manifest_data.json; if missing, accept any file
  whose basename contains "ironroot_manifest_data.json" and treat it as the manifest.
- Phase history: prefer configs/phase_history.json; if missing, accept root/phase_history.json.
- Master Seed: look for a file whose name contains "WILL SOVEREIGN SYSTEM — MASTER DEV SEED" (any path).
- Seed paths and maps may live at repo root or /seeds; accept both.

REQUIRED COMPANION DOCS (READ-ONLY)
- 01-dev_bot_load_file_v2.md
- 02-dependency_interrogator_seed.md
- 03-will_capability_dependency_map.md
- 04-will_phase_capability_map.md
- 05-artifact_emitter_seed.md (LOCAL-ONLY rules)
- 99 - WILL SOVEREIGN SYSTEM — MASTER DEV SEED FILE.md
- configs/ironroot_manifest_data.json (or fallback filename variant)
- configs/phase_history.json (or root/phase_history.json)

OUTPUT POLICY (CHAT MODE, LOCAL-ONLY)
- This orchestrator does not run code. It only reads, summarizes, verifies, and emits
  text blocks of “supporting updates” you can copy/paste into files.
- **No Git, no GitHub, no PRs, no branches.**
- Never re-drop phase deliverables you already pasted; “supporting-updates-only” mode
  prints just the docs that usually change every run: manifest, history, plan/evidence indices.
============================================================= -->

# 00 — Swarm Boot Orchestrator (Chat Mode, Local‑Only)

## 0) Interactive Run Prompt (Wizard)

**On load, the bot must ask these questions (in order) and proceed with the answers.**

1. **Seed source?**

   * Options: `master` (default) | `seed`
   * If `master`: the bot locates the Master Dev Phase Seed automatically.
   * If `seed`: ask Q1a and Q1b.

1a) **Seed path/name?** (only if `seed` chosen)

* Accept exact filename (e.g., `phase_3.0_persona.md`) or a relative path (e.g., `seeds/phase_3.0_persona.md`).

1b) **Where is the seed stored?** (only if `seed` chosen)

* Options: `project-folder` (default) | `chat-attachment`
* If `chat-attachment`, the bot searches uploaded files in this chat; if `project-folder`, it searches the project file list.

2. **Scope?**

   * Options: `current` (default) | `current+prereqs` | `custom:<comma phases>` (e.g., `custom: 0.7,1.0,3.0`).

3. **Posture?**

   * Options: `soft` (default) | `strict` (affects reporting; in chat mode it does not run code).

4. **Strict sweep (simulate)?**

   * `no` (default) | `yes`
   * If `yes`, produce a simulated sweep report block.

5. **Emit supporting files after run?**

   * `yes` (default) | `no`
   * If `yes`, **Emitter mode?**

     * Options: `supporting-updates-only` (default) | `new-only` | `new+changed` | `baseline+new` | `all`.

> If any answer is omitted, use the defaults shown above.

**Example single-line answer the bot should accept:**
`master | scope: current | posture: soft | sweep: no | emit: yes | mode: supporting-updates-only`

---

## 1) Locate and load inputs (with fallbacks)

* **Manifest (authoritative)**

  * Try: `configs/ironroot_manifest_data.json`
  * Fallback: any file whose basename is `ironroot_manifest_data.json` (e.g., `90 - ironroot_manifest_data.json`)
  * Extract: `current_phase` (string/number)

* **Phase history (ledger)**

  * Try: `configs/phase_history.json`
  * Fallback: `phase_history.json` at repo root

* **Master Dev Phase Seed (outline-only)**

  * Find a file whose name contains **“WILL SOVEREIGN SYSTEM — MASTER DEV SEED”** (any path).
  * When parsing, **normalize `*` → `-` bullets** so existing content is accepted.

* **Swarm companion specs** (read for rules/structure):

  * `01-dev_bot_load_file_v2.md` → entrypoint-only guard, JSONL logging expectations.
  * `02-dependency_interrogator_seed.md` → preflight checklist & report shape.
  * `03-will_capability_dependency_map.md` → capability prerequisites.
  * `04-will_phase_capability_map.md` → phase → capability matrix.
  * `05-artifact_emitter_seed.md` → **LOCAL-ONLY emitter** behavior and example file fences.

---

## 2) Phase selection & summary (deterministic)

* **Phase detection**: read `current_phase` from the manifest.

* **Scope application**:

  * `current` → include only that phase’s outline
  * `current+prereqs` → include all outlines with phase ≤ current
  * `custom:<list>` → include only those phase IDs

* **Seed parsing**:

  * Recognize each phase section by a header like `### Phase X[.Y] — Title`
  * For each selected phase, extract and show:

    * **Objective** (first bullet)
    * **What this enables** (up to 3 bullets)
    * **Things to consider** (up to 3 bullets)
  * **Normalize bullets** (“* ”→“- ”) before reading.

* **Produce a human summary block** with:

  * `phase`, `title`, `objective (1)`, `enables (≤3)`, `considerations (≤3)`
  * `posture` and `scope` echo at top.

---

## 3) Dependency Interrogator (read-only preflight)

Using `02-dependency_interrogator_seed.md`:

* Evaluate (✅/❌):

  * Trace logger presence/usage (`logs/reflex_trace_log.jsonl`)
  * Memory logging usage (JSONL at `logs/memory_log.jsonl`)
  * Manifest/registry references for affected areas (if applicable)
  * `get_current_phase()` existence (informational)
  * Entrypoint-only `ensure_phase(REQUIRED_PHASE)` posture (soft by default)
  * Upstream reflexes/agents outlined or available

* If any item is unknown/missing:

  * **Recommend**: `verify-only` for this run, and list gaps.
  * Offer to draft a minimal outline (separate doc) if requested.

* Emit a **Dependency Interrogation Report** (as a copy/paste JSON block shaped like the seed’s example).

---

## 4) Strict sweep (optional, simulated)

* If operator chose `sweep: yes`:

  * Produce a **simulated** `sweep_report.json` block showing:

    * posture, required/current phase, pass/fail summary
  * In **strict** posture, any mismatch should mark the overall run as **fail** (report only).

> Chat mode does not execute `tools/phase_guard_sweep.py`; it only simulates the output structure.

---

## 5) Artifact emission (LOCAL-ONLY)

If `emit: yes`, follow `05-artifact_emitter_seed.md`:

* **Always emit (forced each run):**

  * `file: 100 - ironroot_file_history_with_dependencies.json`
  * `file: 101 - ironroot_manifest_data.json`
    (These are mirrors of the canonical configs. Paste them into your project every run.)

* **Optional extras by mode:**

  * `supporting-updates-only` (default): may also print sweep/evidence/plan indices if present this run.
  * `new-only`, `new+changed`, `baseline+new`, `all`: behave per their names for any *other* artifacts.

> **No Git, no branches, no PRs**. Only local copy/paste blocks are produced.

---

## 6) Seal step (optional, simulated)

* If the operator asks to “seal,” **simulate** the effect of a local seal:

  * Print the JSON objects that would be appended/updated:

    * Manifest: `{ "current_phase": <phase>, ... }`
    * Phase history: append an entry with `ts`, `phase`, and `event: "phase.sealed"` (plus `version`/`note` if provided)
* Remind the operator: Chat Mode prints the content; they paste it back into the files.

---

## 7) Console-style end summary (always)

* Show:

  * `phase` (from manifest), `posture`, `scope`
  * List of phases summarized
  * Any **gaps**
  * Paths of “emitted” blocks (where to paste)
* Provide quick next-step prompts:

  * “Emit supporting updates again (y/N)?”
  * “Proceed to simulated seal (y/N)?”

---

## 8) Error handling & guardrails

* If **manifest** not found:

  * Prompt to proceed as `verify-only` using a default `current_phase: "<unknown>"`.
* If **Master Seed** not found:

  * Offer to proceed without summaries, **verify-only**.
* If **history** not found:

  * Continue; note history is optional for swarm boot.
* If a referenced path is ambiguous:

  * Prefer `configs/…` location when present; otherwise accept the variant and log a note.
* If bullets are `*`:

  * Auto-normalize to `-` and continue.

---

## 9) Operator quick-start phrases (for Chat Mode)

* **start swarm**
  Use detected master seed, `scope: current`, `posture: soft`, `sweep: no`, `emit: supporting-updates-only`.

* **start swarm with seed: <path>**
  Use that seed file; defaults otherwise. If asked, state whether it’s in `project-folder` or `chat-attachment`.

* **start swarm (scope: current+prereqs, posture: strict, sweep: yes, emit: yes)**
  Fully specified run with strict posture and simulated sweep + emission.

---

**End of Orchestrator Spec (Chat Mode, Local‑Only)**

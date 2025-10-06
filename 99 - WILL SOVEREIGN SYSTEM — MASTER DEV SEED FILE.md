# **🧠 WILL SOVEREIGN SYSTEM — MASTER DEV SEED FILE (v1.0)**

**Codename:** FlowMaster\_AI\_WILL\_Stack  
 **Governed by:** IronRoot Law v1.0  
 **Version:** SovereignStack v2.4 → vFinal  
 **Seed Date:** 2025-09-13  
 **Guard Posture:** Soft by default (warn/log); Strict in CI when `WILL_PHASE_STRICT=1`  
 **Authority:** `configs/ironroot_manifest_data.json → current_phase` (manifest is source of truth)

🔐 **CORE PRINCIPLE**  
 "If it’s named, it exists. If it’s referenced, it’s scaffolded. If it’s deferred, it’s locked."  
 This system is intended to avoid guessing, prevent ghosts, and maintain forward compatibility.  
 All modules are expected to be reflex‑scaffolded, phase‑aware at entrypoints, CLI‑testable, and manifest‑bound.

---

## **📜 PHASE BLUEPRINT (0–99)**

### **🧱 PHASE 0–0.6 — IronSpine Core**

* Scaffold intent: memory, manifest, reflex, logging, and CLI tools.

* Locked DB schema (SQLite): manifest, reflex\_registry, memory\_log, boot\_report.

* Phase‑aware behavior expected at entrypoints (soft guard posture).

* Core files (informational references):

  * /core/sqlite\_bootstrap.py

  * /core/memory\_interface.py

  * /core/manifest\_db.py

  * /tools/system\_check.py, /tools/will\_cli.py

  * /reflexes/reflex\_core/reflex\_self\_test\_runner.py

  * /logs/reflex\_trace\_log.jsonl, /logs/memory\_log.jsonl  
    

\#\#\# Phase 0.7 — Local LLM \+ DB-First Retrieval (Outline Only)

\*\*Phase ID:\*\* 0.7

\*\*Owner:\*\* Will Core Team

\*\*Last updated:\*\* 2025-10-03

\--

\#\#\#\# Objective

\- Provide a local assistant that uses a GPU-accelerated LLM through Ollama and prefers the project’s chunk database for answers, with a simple browser UI and citations.

\#\#\#\# What this enables Will to do

\- Answer questions using repo-indexed notes from SQLite as primary context.

\- Fall back to general knowledge when DB context is weak (web fallback planned separately).

\- Present sources as repo-relative paths and chunk indices for transparency.

\- Capture Q/A transcripts to text logs that can be ingested later for growing memory.

\#\#\#\# Examples

\- “What did I plan for the Blue Lake larch trip?” returns items, dates, gear, and a cited chunk path.

\- “Mirror token” prompts echo back a verification string and produce a chat log entry for later ingestion.

\- “Everyday question” prompts can respond without DB context using the local model’s general knowledge.

\#\#\#\# Things to consider

\- Phase language treated as metadata; strict enforcement planned for sealing only.

\- GPU acceleration expected to be active on supported NVIDIA cards via Ollama.

\- HTTP interface expected to remain stable at http://127.0.0.1:11434 for model calls.

\- Ask endpoint expected to remain at http://127.0.0.1:8766 for the local UI.

\- Non-goal: cloud APIs and online search integrations at this phase.

\- Non-goal: multi-user auth, sessions, or role-based access at this phase.

\#\#\#\# Inputs / Prerequisites

\- Referenced docs or configs (expected to exist or be planned), e.g., configs/ironroot\_manifest\_data.json

\- Prior decisions or maps (expected to be accessible), e.g., configs/phase\_history.json

\- Example files for context (not created by this phase), e.g., tools/retriever.py, tools/model\_router.py, tools/ask\_will.py, tools/ask\_server\_mirror.py, ui/willchat/index.html

\#\#\#\# Acceptance (human view)

\- A reviewer can describe the end-to-end outcome in one short paragraph.

\- Intended routing and citation behavior is clear from the examples and constraints.

\- Open questions and assumptions are listed or confirmed with the owner.

\#\#\#\# Risks / Guardrails

\- Phase drift risk addressed by soft checks and strict sealing passes.

\- Local GPU dependency can impact performance on unsupported hardware.

\- Data hygiene risk mitigated by chunk de-duplication and stable hashing strategy.

\#\#\#\# References

\- chunk\_store.db schema and usage notes in tools/chunker/\*

\- UI context at ui/willchat/index.html

\- Logging and trace conventions at logs/\* and core/trace\_logger.py

------

\- Phase ID: 0.8

\- Phase Title: Soft Phase Guard adoption

\- Owner: Will Operator

\- Last updated: 2025-10-03

\- Objective: Establish a soft phase posture that warns in development and supports strict checks in CI without blocking imports.

\- What this enables Will to do:

\- Provide a single authority path for the current phase using environment, manifest, and history as context.

\- Issue structured warnings when phase mismatches are detected during entrypoint checks.

\- Toggle strict posture through an environment flag for CI and sealing use cases.

\- Produce deterministic planning artifacts that reference the soft guard posture.

\- Examples:

\- A developer starts a CLI entrypoint and receives a non-blocking warning when the required phase differs from the current phase.

\- A CI job enables strict posture and receives a clear failure with a JSON summary when phases differ.

\- The planning layer indexes a seed and records posture details in plan metadata for auditing.

\- Things to consider:

\- Library modules are expected to remain import-safe with no phase checks inside the module body.

\- Entrypoints are expected to perform phase awareness and emit warnings or strict errors based on posture.

\- Logs are expected to use JSON Lines with consistent keys for tracing and audits.

\- Phase values are expected to be sourced from a single location to avoid drift.

\- Non-goal: introduce hard gating inside shared libraries.

\- Non-goal: modify production data paths during local development.

\- Inputs / Prerequisites:

\- Example reference: configs/ironroot\_manifest\_data.json for the current phase value.

\- Example reference: configs/phase\_history.json for historical context.

\- Example reference: logs/reflex\_trace\_log.jsonl and logs/phase\_guard\_log.jsonl for posture breadcrumbs.

\- Acceptance (human view):

\- A reviewer can summarize the soft posture and describe how development differs from CI in one short paragraph.

\- The enablement points and examples make the behavior clear without reading code.

\- Open questions and assumptions are listed for the owner to confirm.

\- Risks / Guardrails:

\- Risk: posture drift between local and CI; mitigation: surface posture and phase values in every entrypoint message.

\- Risk: inconsistent logging schema; mitigation: document stable keys and lint JSON Lines during reviews.

\- Guardrail: posture changes are proposed in planning artifacts and linked to evidence for verification.

\- References:

\- Example doc: seeds/Soft Phase Guard seed file.md for the posture definition.

\- Example doc: seeds/02-dependency\_interrogator\_seed.md for preflight checks.

\- Example map: seeds/03-will\_capability\_dependency\_map.md for capability posture context.

---

Phase 0.81

<!-- RESET: This file replaces all previous phase formatting templates. -->

<!-- ENFORCE: Use only "- " dash bullets. Reject "*", numbers, checkboxes in output. -->

<!-- =============================================================
OUTLINE-ONLY PHASE FILE (FOR SWARM CONTEXT) — STRICT / NON‑EXECUTABLE
Purpose: This is a human/swarm brief ONLY. The executor ignores this file.
Do NOT include Plan Blocks, Steps, Acceptance Checks, code, or commands.

BULLET / FORMAT RULES (BOT MUST FOLLOW)
- Use dash bullets only: "- ". Never use "*", numbers, or checkboxes in this file.
- One idea per bullet. Keep sentences short and declarative.
- Use plain text only. No code blocks, no CLI commands.
- Give response in a Code Block.

NON-EXECUTABLE LANGUAGE GUARD + AUTO-LINT
❌ BANNED (case-insensitive): must, shall, ensure, required to, need to,
   will create, will scaffold, will write, will deploy, will merge,
   run, execute, build, scaffold, generate, deploy, merge, write code,
   “will be created at <path>”
✅ PREFERRED: expected to, intended to, planned to, may, can,
   verify, read, assess, plan, outline, propose,
   example/reference paths (context only), not targets

AUTO-REWRITE POLICY (BOT MUST APPLY BEFORE OUTPUT)
1) Replace banned terms using this map (exact, case-insensitive):
   - must|shall|ensure|required to|need to  -> expected to
   - will create|will scaffold|will write   -> intended to
   - run|execute|build|scaffold|generate    -> plan/assess (choose best fit)
   - deploy|merge                           -> propose (for later review)
2) Remove any CLI/code blocks (```…```); rewrite as plain English.
3) If ANY banned term remains after rewrite -> FAIL and ask user to approve replacements.

BOT PROMPTS (ASK USER ONLY FOR):
1) Phase ID (e.g., 1.3) and Human Title
2) Owner and Today’s date (YYYY‑MM‑DD)
3) One‑sentence Objective
(Everything else can be drafted from research; keep wording non‑executive.)

DATA HYGIENE
- If referencing files, use repo‑relative paths as examples only.
- Avoid imperative phrasing; keep guidance/context tone throughout.
============================================================= -->

### Phase 0.8-prep — Phase 0.7 wrap, git hygiene, and 0.8 preparation
**Phase ID:** 0.8-prep
**Owner:** Mark Davis
**Last updated:** 2025-10-04

---

#### Objective

* Capture the current state after sealing 0.7.
* Stabilize repository hygiene for future phases.
* Prepare a clean baseline for upcoming 0.8 work without triggering swarm actions.

#### What this enables Will to do

* Reference a sealed 0.7 state for provenance and audit.
* Work from a clean branch for 0.8 preparation activities.
* Emit small artifacts from seeds as a sanity check without side effects.
* Trace important actions in reflex logs for later review.

#### Examples

* Example reference: a sealed tag exists for 0.7 (e.g., v0.7.0-sealed) for reproducibility.
* Example reference: a branch such as phase-0.8-dev-clean exists for preparation.
* Example reference: artifacts contain PhasePlan.json and plan_lock.json for planning context.

#### Things to consider

* Phase 0.8 is not started in this outline. The focus is preparation only.
* Language stays non-executive and avoids imperative phrasing and commands.
* Example paths appear as context only (e.g., configs/ironroot_manifest_data.json).
* Logs referenced for context only (e.g., logs/reflex_trace_log.jsonl lines that indicate actions).
* Non-goal: no swarm orchestration for 0.8 in this step.
* Non-goal: no schema or API expansion in this outline.

#### Inputs / Prerequisites

* Example sealed state present in configs/phase_history.json and configs/ironroot_manifest_data.json.
* Example tag present on origin (e.g., v0.7.0-sealed) for external provenance.
* Example planning files present in artifacts/PhasePlan.json and artifacts/plan_lock.json.

#### Acceptance (human view)

* A reviewer can summarize the 0.7 wrap and repository hygiene in one short paragraph.
* The repository baseline for 0.8 preparation is clear and references the sealed tag and clean branch.
* Open questions are listed for owner confirmation before moving to an active 0.8 phase.

#### Risks / Guardrails

* Risk: unintended changes in master or preparation branch during clean-up.
* Guardrail: use preparation branches to isolate work and protect the sealed tag state.
* Guardrail: keep artifact emission seeds minimal and context-only to avoid unintended side effects.

#### References

* Example manifest reference: configs/ironroot_manifest_data.json for current_phase and current_version context.
* Example phase history reference: configs/phase_history.json for historical entries.
* Example artifacts reference: artifacts/PhasePlan.json and artifacts/plan_lock.json for planning context.












### **🧠 PHASE 1–2 — Reflex Brainstem \+ Planning Core**

* Reflex loading system (outline).

* Reflex memory tagging (`#reflex:<name>`, `#task:<type>`, `#phase:<id>`).

* Goal chain planning and prioritization (outline).

* Local goal plan persistence (outline).

### **🪪 PHASE 3–5 — Persona Layer \+ Agent Identity**

* Agents as modular personas (Planner, Analyst, Support, etc.).

* Each agent expected to include:

  * Reflex routing entry\_point.

  * Persona profile (tone, role, memory filter).

  * Memory silo tagging: `#persona:<id>`, `#agent:<name>`.

* CLI agent runner and persona switcher (outline).

### **⚙️ PHASE 6–10 — Reflex Toolchains \+ Job Delegation**

* Reflex agent delegation via `reflex_agent_delegate()` (outline).

* CLI intents: `run_agent`, `list_agents`, `delegate_goal "<task>"`.

* Persona‑tuned routing informed by `persona_tone_rules.json` (outline).

### **🧬 PHASE 11–20 — Memory Fitness \+ LLM Routing**

* Memory‑conditioned prompt construction.

* Reflex memory filtering by tag, role, source.

* Stubs for `ask_gpt()` and `reflex_goal_gpt_route.py` expected from Phase 0 if referenced.

* For any Phase 11+ references, placeholder stubs are expected if not implemented.

### **🔌 PHASE 21–30 — Multi‑Agent Council \+ Persona Council Layer**

* Reflex agents intended to vote, hand off tasks, and act independently.

* GUI: agent switcher panel (outline).

* `persona_profiles.json` defines behavior, tone, access scope (outline).

### **🧠 PHASE 31 — LLM\_Brainstem (Local Model Layer)**

* Local fallback (e.g., GPTQ/Mistral) intended.

* `ask_gpt()` may resolve to a local model when external API unavailable.

* Memory→prompt conditioning enabled (outline).

### **🎛️ PHASE 32 — SnapApp GUI \+ Panel Filters**

* Snapshot of current memory state (outline).

* GUI‑based reflex runner, filter toggles, role‑color themes.

* GUI panels are expected to be scaffolded as placeholders when referenced.

### **🧪 PHASE 33 — Self‑Diagnostic Reflex Layer**

* `reflex_self_test_all()` scans Will’s brain (outline).

* Suggests repairs or proposes safe scaffolds for missing stubs.

* Findings logged to `logs/reflex_error_log.jsonl` (if present).

### **🧠 PHASE 34 — Persona Tone Shaping**

* Agents can speak in developer, support, or analyst tone (outline).

* Persona filters applied via `persona_profiles.json` (outline).

### **🔌 PHASE 35 — Plugin Interface \+ API Launcher**

* Reflexes may trigger plugins (send\_sms, query\_google) via wrappers.

* Plugin registry and auto‑load behavior (outline).

### **🧱 PHASE 36–98 — Advanced Goal Engine \+ Evolution**

* Meta‑agent clustering (outline).

* Will↔Will communication mesh (multinode) (outline).

* Long‑term pattern memory and self‑tuning (outline).

### **💥 PHASE 99 — Sovereign Funbox**

* Always‑on voice commands (outline).

* Calendar and travel helper (outline).

* Humor, commentary, and emotion mirroring (outline).

---

## **📦 CORE STRUCTURE (reference layout)**

* /core/ → memory, manifest, db, boot logic

* /reflexes/ → reflexes, agents, council, tracing

* /tools/ → CLI wrappers

* /gui/ → FastAPI panels, APIs, switches

* /configs/ → static configs, phase‑aware

* /sandbox/ → test reflexes and CLI runners

* /logs/ → outputs: memory, trace, test, boot (JSONL preferred)

---

## **✅ REQUIRED FILE POLICIES (soft‑guard aligned)**

* Phase awareness is enforced at **entrypoints** (CLIs/servers) using `ensure_phase(REQUIRED_PHASE)`; libraries remain import‑safe.

* CLI‑testable intent: tools/reflexes are planned to expose `run_cli()` where appropriate.

* Memory logging intent: executions are expected to call a memory‑logging utility (e.g., `log_memory_event`).

* Manifest registration intent: referenced files are expected to appear in `ironroot_manifest_data.json` when promoted.

* Stub safety: if a reflex is not implemented, a clear placeholder is expected to exist (documentation or safe stub).

* JSONL log convention preferred for trace and memory.

### **🧠 FILE SAFETY SCHEMA (patterns; guidance)**

* **Reflex Stub** (if future phase): returns a clear "🚧 not implemented yet" message without side effects.

* **CLI Tool**: `run_cli()` entry with trace/memory logging hooks.

* **GUI Route**: surface route with error‑tolerant wrapper.

These patterns are examples for clarity; they are not executable mandates in this master seed.

---

## **🔹 PHASE 0.7 — TraceSync & Reflex Audit (detailed example)**

**Phase Class:** IronSpine Hardening  
 **Current Status:** SEED READY  
 **Phase Hash:** 0.7\_TRACESYNC\_REFLEXAUDIT  
 **Parent:** 0.6 – Reflex Memory Trace Lock  
 **Next:** 0.8 – Reflex Routing and CLI Coverage Map

### **Primary Objectives (outline)**

* Reflex ↔ CLI link validation intended so each reflex can be invoked by a CLI and vice versa.

* Trace consistency review intended so CLI calls produce reflex \+ dual logs (trace and memory).

* Reflex audit reporting intended (`tools/reflex_coverage_report.py` outline).

* Stub isolation intent: identify unimplemented reflexes and document them clearly.

* Logging tripwire intent: highlight any missing trace/memory events for review.

### **Informational file references (create/update outside this seed)**

* tools/reflex\_coverage\_report.py — outline for a scanner that compares registry to manifest and emits a JSON report.

* tests/test\_phase\_0\_7\_trace\_sync.py — outline for validating trace consistency across CLI and reflex chains.

* reflexes/reflex\_core/reflex\_self\_test\_runner.py — outline for a runner that dual‑logs in test mode.

* core/reflex\_trace\_validator.py — optional helper outline for trace validation logic.

* configs/reflex\_stub\_list.json — registry outline of reflexes planned but not implemented.

* sandbox/reflex\_test\_manifest\_snapshot.json — snapshot outline of reflex/CLI/trace/test coverage.

### **Phase‑specific guidance**

* Reflexes referenced under `reflexes/` are expected to appear in the manifest and file history when promoted.

* Phase posture expected to be soft at runtime; strict checks intended for CI/seal flows.

* CLI dispatch logic is expected to be scan‑friendly (no hidden routing).

### **Example report shape (for context)**

{  
  "reflex": "reflex\_trace\_ping",  
  "registered\_in\_manifest": true,  
  "listed\_in\_file\_history": true,  
  "has\_cli\_binding": true,  
  "phase\_aware\_entrypoint": true,  
  "logs\_memory": true,  
  "logs\_trace": true,  
  "stubbed": false,  
  "testable": true  
}

---

## **🧱 Phase Expectations Summary (global intent)**

* Reflex dual logging expected (trace \+ memory).

* Phase awareness handled at entrypoints (soft by default; strict in CI).

* CLI dispatch coverage expected to be mapped and testable.

* Stubbed reflexes expected to be clearly listed when not implemented.

* UTF‑8 JSON/JSONL writes expected for auditability.

* Canonical reflex template is a recommended reference for consistency.

---

## **🔐 Entrypoint Phase Awareness Pattern (replace hard locks)**

* Entrypoints (CLIs/servers) call a guard like `ensure_phase(REQUIRED_PHASE)`.

* Default posture is soft (warn \+ log); strict under `WILL_PHASE_STRICT=1` or CI.

* Libraries do **not** raise at import time; they remain usable across phases.

* The manifest’s `current_phase` is the single authority; history is a ledger; overrides are diagnostic only.

---

## **🧠 Behavior Summary (post‑build vision)**

* Accept natural‑language goals with reflex routing.

* Run CLI/GUI tools via deterministic dispatch and logging.

* Log all actions to memory and trace logs.

* Chain multiple reflexes to fulfill multi‑step tasks.

* Self‑test and audit via reflex testing and trace tools.

* Plan next steps using tagged memory and planner outlines.

* Propose self‑repair steps in later phases.

* Support WillClone orchestration with isolated memory in later phases.

---

## **📘 Notes to operators**

* To begin a swarm run, you may say **“start swarm”** or **“start swarm with seed: ”**.

* Use the **Artifact Emitter** in `supporting-updates-only` mode to print supporting changed files for copy/paste (manifest/history/plan/sweep/evidence index).

* For sealing in CI or locally, prefer the dedicated seal runner; strict posture intended for seals.

---

## **🧾 Changelog (human)**

* v1.0 — Soft‑guard alignment; dash‑only bullets; non‑executable language; entrypoint‑only enforcement; JSONL log standard; preserved full phase blueprint and tables in outline form.

**End of Master Dev Seed (v1) — SWARM EDIT**


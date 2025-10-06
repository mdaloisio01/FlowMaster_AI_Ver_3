# 🧠 Will Sovereign Stack — Dependency Interrogator Seed (Soft Phase Guard–Aligned)

**Seed Type:** Self‑Bootstrapping Dependency Scaffold
**Use With:** Any Dev Bot, GPT Agent, or Deep Research Bot working on Will
**Phase Posture:** **Phase‑Neutral** (works on Day 1 or Day 10,000) — **Soft Phase Guard compatible**

> Purpose: stop AI from guessing or jumping ahead. **Confirm what exists, identify gaps, and only then propose/build.**

---

## 🛡️ Intent

This seed forces the bot into **Interrogator Mode** *before* any build or code generation. It must:

1. Validate the required building blocks exist.
2. If anything is missing/uncertain, **pause** and propose fixes or ask you concise questions.
3. Only proceed to planning/building **after** preconditions are satisfied (or you explicitly accept verify‑only mode).

---

## 🔒 Phase Guard Alignment (authoritative rules)

* **Authority for current phase:** `configs/ironroot_manifest_data.json → current_phase` (manifest is the source of truth).

  * `configs/phase_history.json` is a **ledger only** (never authoritative).
  * Optional **diagnostic override**: `WILL_PHASE_OVERRIDE` (logged, not authoritative).
  * **Strict posture** in CI/seal: `WILL_PHASE_STRICT=1` → fail fast on mismatch.
* **Enforcement location:** **entrypoints only** (CLIs/servers) via `ensure_phase(REQUIRED_PHASE)`. Libraries must remain import‑safe (no hard checks inside `core/*`, `reflexes/*`, etc.).

---

## 🔍 Interrogator Checks (the questions the bot MUST ask/verify)

**Say you ask:** “Build a WillClone reflex.”
**Bot must respond:** “Let me confirm the pieces that should already exist.” Then it must verify:

* Do you have a working **trace logger** that writes JSONL (e.g., `logs/reflex_trace_log.jsonl`) and is called on every reflex/tool?
* Do your reflexes where appropriate call **`log_memory_event()`** for memory tracking (JSONL to `logs/memory_log.jsonl`)?
* Are **manifest** entries (and, if applicable, **reflex registry** entries) **present and current** for the code being introduced?
* Does **`get_current_phase()`** exist, return the manifest phase, and is it used for display/logs?
* Do **entrypoints** (CLI/server start) call the **soft phase guard** `ensure_phase(REQUIRED_PHASE)` that **warns by default** and is **strict only when `WILL_PHASE_STRICT=1`**?
* Have the **lower‑level reflexes/agents** required for this feature already been designed (or at least outlined) so we know what to integrate with?

**If anything is missing or unknown:** the bot must **stop**, summarize the gap, and either (a) propose a minimal fix plan, or (b) switch to **verify‑only mode** for this session.

---

## 📚 Inputs the bot should load (read‑only)

* `configs/ironroot_manifest_data.json` (read `current_phase`)
* `configs/phase_history.json` (for context only; not authoritative)
* `reflex_registry.json` (if your repo uses one)
* Capability/phase maps (if present):

  * `seeds/04-will_phase_capability_map.md`
  * `seeds/03-will_capability_dependency_map.md`
* Any utility exposing `get_current_phase()`

If any input is missing, the bot asks whether to draft a **placeholder outline** (documentation only) or to proceed **verify‑only**.

---

## 🧩 Template the bot must fill (report, not code)

**Requested Capability / Intent:** *<what you asked for>*

**Dependency Interrogation Report**

* Trace logger present & used: ✅/❌
* Memory logging (`log_memory_event`) appropriate & used: ✅/❌
* Manifest/registry entries present for affected code: ✅/❌
* `get_current_phase()` available & returns manifest phase: ✅/❌
* Entrypoints guard with `ensure_phase(REQUIRED_PHASE)` (soft by default): ✅/❌
* Upstream reflexes/agents outlined or available: ✅/❌

**Gaps & Decisions**

* Gaps detected: *<list or “none”>*
* Proposed path: *verify‑only | draft outline for missing X | request owner confirmation on Y*
* Owner decision: *accepted | needs follow‑up*

**Outputs (artifacts are reports only, no code)**

* `artifacts/interrogator/<run_id>/dependency_report.json`
* `artifacts/interrogator/<run_id>/notes.md`
* (optional) `artifacts/evidence/<plan_hash or run_id>/index.json` when verification requires external corroboration.

> ⚠️ This seed **does not** authorize builds. It only produces a report and a recommendation. Build steps require a **separate** approved plan (e.g., a Plan Block compiled by the Plan Indexer).

---

## ❌ Do Not Allow

* Reflexes without `log_memory_event()` where appropriate.
* Tools without `trace_logger` calls.
* Code that isn’t represented in the manifest/registry when required.
* Bots that plow ahead when preconditions are unknown — they must pause and summarize.

---

## 🔧 Soft Phase Guard Notes (recap)

* Runtime code should **not** hard‑enforce phase inside libraries; checks live in **entrypoints only**.
* Default behavior: **warn & log** on mismatch (continue).
* Strict behavior for CI/sealing: set `WILL_PHASE_STRICT=1` to **fail fast**.
* Keep phase values in the **manifest**; history is a ledger; overrides are diagnostic.

---

## 🧭 How the swarm uses this seed

1. **Preflight** — Bot loads inputs and asks the **Interrogator Checks** above.
2. **Assess** — It fills the **Dependency Interrogation Report** with ✅/❌ per item.
3. **Decide** — If all green: propose next‑step planning (not code). If gaps: recommend verify‑only or a tiny outline to address the gap.
4. **Record** — It writes `dependency_report.json` and optional evidence for audit.
5. **Stop (unless approved)** — No code generation until you explicitly approve a build plan in a separate seed/plan.

---

## 📎 Example: `dependency_report.json`

```json
{
  "ts": "2025-10-03T20:19:00Z",
  "intent": "WillClone reflex",
  "phase": {"current": "3.0", "posture": "soft"},
  "checks": {
    "trace_logger": true,
    "memory_logging": true,
    "manifest_registry": false,
    "get_current_phase": true,
    "entrypoint_guard": true,
    "upstream_ready": false
  },
  "gaps": [
    "No manifest/registry entry for willclone_reflex",
    "Planner dependency not outlined"
  ],
  "recommendation": "verify-only",
  "notes": "Create outline for planner dependency before any build."
}
```

---

*Seed End*

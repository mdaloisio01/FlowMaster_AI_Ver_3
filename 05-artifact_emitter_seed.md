# Artifact Emitter Seed — Always emit 100 & 101 (Chat Mode)

> Purpose: at the end of **every** swarm run, always print copy‑paste blocks for the two mirror files used in ChatGPT mode:
>
> * **100 - ironroot_file_history_with_dependencies.json**
> * **101 - ironroot_manifest_data.json**
>
> This seed is phase‑neutral and safe for soft‑guard use. It does not run code; it only defines what to emit as text blocks.

---

## How this seed is used

* In ChatGPT mode, the swarm’s **emitter step** reads this file and prints the fenced blocks below.
* You copy each block and paste it into the matching file path in your project folder.
* These two files are **always emitted** regardless of emitter mode, so they stay in sync every phase.
* Other artifacts are optional and controlled by the emitter mode.

---

## Emitter behavior (Chat Mode)

* **Always‑on mirrors (forced):** the two fences for **100** and **101** are printed every run.
* **Modes (optional extras):**

  * `supporting-updates-only` (default): may also print sweep/evidence/plan indices if present this run.
  * `new-only`, `new+changed`, `baseline+new`, `all`: behave per their names for any *other* artifacts.
* **Normalization:** if the canonical files exist under `configs/…`, the swarm emits their **current content** mirrored into **100/101**. If the canonical files are missing, it emits the **best available** (existing 100/101 with updates from the run summary where possible).

---

## Canonical sources (where to mirror from)

* **Manifest (canonical):** `configs/ironroot_manifest_data.json` (fallback: any file whose basename equals that).
* **File history (canonical):** `configs/ironroot_file_history_with_dependencies.json` (fallback: any file whose basename equals that).

> Chat Mode rule: The bot should prefer `configs/…` content and mirror it into the 100/101 filenames below.

---

```file: 100 - ironroot_file_history_with_dependencies.json
{{MIRROR_FROM canonical="configs/ironroot_file_history_with_dependencies.json"
              fallback="100 - ironroot_file_history_with_dependencies.json"
              note="This is a full JSON mirror. Keep keys order and formatting stable where possible."}}
```

```file: 101 - ironroot_manifest_data.json
{{MIRROR_FROM canonical="configs/ironroot_manifest_data.json"
              fallback="101 - ironroot_manifest_data.json"
              note="Mirror the complete manifest, including current_phase, manifest lists, files, and phase_history."}}
```

---

## Optional supporting artifacts (only printed if your emitter mode includes them)

```file: artifacts/reports/sweep_report.json
{{IF_SWEEP_AVAILABLE then_emit_current_sweep_report_else_skip}}
```

```file: artifacts/evidence/{{RUN_ID}}/index.json
{{IF_EVIDENCE_AVAILABLE then_emit_current_evidence_index_else_skip}}
```

```file: artifacts/plan_lock.json
{{IF_PLAN_LOCK_AVAILABLE then_emit_current_plan_lock_else_skip}}
```

---

## Operator notes (non‑dev)

* After a run, you should always see two blocks for **100** and **101**. Paste them back into your project.
* If you also enabled extras (sweep/evidence/plan), paste those where shown by the `file:` line.
* If the bot warns that a canonical file is missing, it will still emit the best available content; fix the canonical file when you can.

---

## Changelog (seed file)

* v1.1 — **Always‑on mirrors** for 100 & 101. Normalization and fallbacks clarified.
* v1.0 — Initial emitter sample.

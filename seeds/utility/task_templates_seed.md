# task_templates_seed.md

## Purpose

This seed defines the structure, usage rules, and management policies for YAML-based task templates used by Will to automate internal operations and external workflows. Templates provide a reusable, modular way to define actions, reflex sequences, and logic that Will can execute based on schedules, triggers, or commands.

---

## 🧠 Core Concepts

- **YAML Templates** are mini-execution blueprints written in YAML format that tell Will *what to do* and *how to do it*.
- Templates can trigger reflexes, run scripts, post alerts, ingest files, or manage workflows.
- Templates can be triggered manually, scheduled, or called by other templates (chained logic).

---

## ✅ Supported Template Features

- `name`: Human-readable task name
- `description`: Clear explanation of what the template does
- `version`: Semantic version of the template (e.g., 1.0.2)
- `tags`: For grouping/batch execution (e.g., maintenance, backup)
- `reflex_chain`: List of reflexes or actions Will should run
- `conditions`: Optional logic (e.g., only run if memory_load < 0.75)
- `time_window`: Optional execution window (e.g., weekdays 1am–3am)
- `fallbacks`: Optional backup template or retry strategy
- `log_metadata`: Will auto-attach execution logs (time, success/failure, duration)

---

## 🔄 Template Versioning Rules

- Each template includes a `version`.
- Will compares the live version vs. last-used version.
- If outdated, Will can:
  - Auto-update it (if allowed)
  - Prompt user for approval
  - Flag it as deprecated

---

## 🏗 Template Inheritance

Templates may use `extends: base_template_name` to inherit base behaviors and override only needed fields. This avoids redundancy and simplifies updates.

---

## 🛡 Execution Safeguards

- Templates can include `max_runtime`, `expected_output`, or `quarantine_on_error` flags.
- Will will quarantine failing templates automatically if they repeatedly fail.

---

## 🧩 Template Tags

Used to group or filter for batch operations. Examples:
- `daily`, `startup`, `maintenance`, `user-triggered`, `emergency`

---

## 🧑‍💻 Human-readable Explainability

Will must be able to explain any template by summarizing:
> “This template runs every day at 3am, clears memory bloat, compresses logs, and sends a health report.”

---

## 📦 File Location & Format

- All templates live in `/templates/` directory inside Will’s runtime.
- Each is saved as `taskname.yaml`.
- Templates must validate against Will’s internal schema before execution.

---

## 🔧 GUI Support (Future)

Templates will eventually be editable via GUI:
- Field-aware inputs (e.g., dropdowns, booleans)
- Version rollback
- Description auto-fill
- Execution history viewer

---

## 🧠 Memory Integration

Will logs every execution with:
- Template ID
- Start/finish timestamps
- Result status
- Runtime duration
- Output summary
- Trigger type (manual, scheduled, reflex)

This log is available in the `template_execution_log` memory channel.

---

## 🤝 Reflex Interop

- Templates may include direct `reflex_id`s
- Reflexes may return variables used in template logic
- Supports nested templates (1 template can call another)

---

## 👁 Example Template

```yaml
name: Daily System Maintenance
version: 1.2.0
description: Performs daily memory optimization, log rotation, and disk cleanup.
tags: [daily, maintenance]
reflex_chain:
  - optimize_memory
  - rotate_logs
  - cleanup_temp_files
conditions:
  memory_load: <0.75
time_window:
  start: "01:00"
  end: "03:00"
fallbacks:
  on_failure: retry_maintenance.yaml
log_metadata: true
```

---

## 🚫 Disabled Templates

Templates with `enabled: false` will not run under any condition, and Will will explain why.

---

## 💬 Will’s Summary Capability

Any time a user asks:
> “What does this template do?”
Will can generate a plain-English explanation of the workflow, conditions, and timing.

---

## Final Notes

- Will never runs unvalidated templates.
- Template changes are tracked.
- Advanced scripting features (loops, variables) may be added later as needed.


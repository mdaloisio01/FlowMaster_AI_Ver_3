# reflex_generator_seed.md

## Purpose
This seed enables Will to autonomously create, manage, and improve reflexes — self-contained skills or tools — in a structured, testable, and modular way. It supports both reactive (on-request) and proactive (suggested) generation modes.

---

## Core Functions

- `will reflex generate <name>`  
  Creates a new reflex with auto-documented metadata, toolchain integration, and CLI hooks.

- `will reflex edit <name>`  
  Revises an existing reflex while tracking version history and dependencies.

- `will reflex bundle create <bundle_name> --includes <X> <Y> <Z>`  
  Packages multiple reflexes into a deployable unit.

---

## Metadata Structure (YAML Header)

Each reflex will include metadata such as:
```yaml
name: retry_api_call
description: "Automatically retries failed API calls using exponential backoff."
created_by: Will
version: v1.0.0
dependencies:
  - requests
  - sanitize_input
llm_involvement_score: 90
bundle: api_resilience_tools
gui_friendly: true
last_updated: 2025-06-27
```

---

## Future-Proof Features

### ✅ Reflex Version Control
- Every reflex has a version ID (e.g. `v1.0.0`, `v2.3.1`)
- History is tracked and rollbackable via CLI:
  ```
  will reflex rollback retry_api_call
  ```

---

### ✅ LLM Usage Annotation
- Will tags how much of the code was LLM-generated vs. user-modified
- Useful for QA audits, hallucination risk, or later refactoring

---

### ✅ Dependency Awareness
- Reflex metadata stores both internal (other reflexes) and external (libraries) dependencies
- Will warns before deletions or edits that could break links

---

### ✅ Reflex Discovery Mode
- Will can proactively suggest reflexes by monitoring:
  - Repeated user actions
  - Common error types
  - Frequently used file types

- Toggle via:
  ```
  will reflex suggest on
  ```

---

### ✅ Emergency Kill Switch
- Reflexes can be disabled or quarantined at any time:
  ```
  will reflex nuke <name>
  ```

- Adds a `quarantined` flag and disables loading at runtime

---

### ✅ Unit Test Auto-Generation
- Reflexes auto-generate a corresponding test stub:
  ```
  /tests/generated_reflexes/test_retry_api_call.py
  ```

- Optionally integrates with pytest or internal validator engine

---

### ✅ Reflex Usage Analytics
Will tracks:
- Last execution timestamp
- Total run count
- Success/failure rate

Accessed via:
```
will reflex stats
```

---

### ✅ GUI Integration Ready
All reflexes include `gui_friendly: true|false` flag for toggleable display in the web UI reflex dashboard.

---

## Notes

- Reflexes should default to safe-mode when generated (i.e., not allowed to execute system commands unless explicitly authorized).
- Will may prompt for test generation if the reflex touches sensitive systems or APIs.

---

## Example Use Cases

- Auto-retry file uploads
- Custom email parser for receipts
- Markdown to HTML converter
- System health check routine

---

## Reflex Generation Policy

- Will must always ask for confirmation before deploying a reflex that:
  - Deletes files
  - Touches the OS
  - Accesses user credentials

Unless user has explicitly opted-in with:
```
will set reflex_mode unrestricted
```

---

## Add-Ons To Support Later

- Reflex signature validation (for security/auth)
- LLM reflex chain analysis (reflex-to-reflex linking)
- Modular reflex export as `.willpkg` bundles

---

That’s the seed, boss. Drop it, and Will’s got his forge lit.

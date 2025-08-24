# reflex_sandbox_seed.md

## Purpose
The Reflex Sandbox is a controlled environment where new or updated reflexes can be safely tested, debugged, and optimized before being promoted into Will’s production reflex catalog. It ensures safety, stability, and rapid iteration.

---

## Core Features

### ✅ Isolated Testing
- Reflexes in the sandbox cannot affect production data or systems.
- They can only access mock memory, test datasets, and simulated outputs.
- Output is logged and annotated with success/failure status.

### 🧪 Multi-Environment Testing
- Reflexes can be run with simulated inputs from different environments (e.g., dev vs prod).
- Supports mock datasets and test-specific variables.

### 🔁 Simulation Mode
- Reflexes can be run in "simulate only" mode that previews behavior without executing real logic.
- GPT summarizes expected behavior based on the reflex’s intent and logic structure.

Example:
```bash
reflex sandbox simulate summarize_invoice
```

### 📡 Remote Access
- Reflexes can be submitted to the sandbox via API:
  `POST /reflex/sandbox`
- Remote submission must include a valid API token.
- Reflex outputs and logs can be retrieved via `/reflex/sandbox/:id/result`.

---

## Reflex Promotion Protocol

Reflexes in the sandbox must pass:
1. A valid test suite (`/tests/reflex/<name>_tests.py`)
2. Simulated review of edge cases
3. Resource load analysis (see below)
4. Security scan (auto-code reviewer)
5. Optional: human approval (if flagged as high-risk or generated autonomously)

Only then are they promoted using:
```bash
reflex promote summarize_invoice
```

---

## Version Control

All sandbox reflexes support semantic versioning.

Example:
```bash
reflex sandbox diff summarize_invoice v0.1.3 v0.1.4
```

Changelogs and diffs are stored in `/reflex_sandbox/history/<reflex_name>/`.

---

## Reflex Classifications

Reflexes must be tagged with one of the following:
- `trusted` – safe for autopilot usage
- `restricted` – can only run with human approval
- `admin-only` – critical systems
- `auto-generated` – built by Will’s reflex builder and pending review

---

## Performance Tracking

Each reflex logs:
- Execution time
- Memory used
- Token usage (if LLM involved)
- Return size
- Failures / edge case rejections
- Runtime warnings

These are stored in `/reflex_sandbox/performance/` and available via CLI:

```bash
reflex metrics summarize_invoice
```

---

## Reflex Permissions

Autonomous reflex generation (Reflex Builder) can generate testable logic but must:
- Use sandbox only
- Mark output as `auto-generated`
- Notify operator for approval

---

## Notes
- Sandbox testing will eventually support version pinning for dependency management (e.g., specific GPT models, packages).
- Reflexes that pass sandbox testing can optionally be added to auto-regression testing before promotion.

---

## CLI Commands

- `reflex sandbox run <reflex>`
- `reflex sandbox simulate <reflex>`
- `reflex sandbox diff <reflex> vX.Y.Z vX.Y+1`
- `reflex metrics <reflex>`
- `reflex promote <reflex>`

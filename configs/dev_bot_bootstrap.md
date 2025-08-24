# 🧠 FlowMaster AI — Dev Bot Bootstrap Protocol
**File:** `dev_bot_bootstrap.md`  
**Scope:** Phase 0–∞  
**Law:** IronRoot Law v1.0

---

## 🔐 PRIMARY OBJECTIVE
Establish a modular, secure, traceable AI OS built on:
- ✅ SQLite-backed state (will_data.db)
- ✅ Reflex execution safety
- ✅ CLI/GUI parity (CLI first)
- ✅ Phase-lock + manifest registration
- ✅ Self-healing + testable architecture

---

## 🧱 IRONROOT ENFORCEMENT CORE
| Component | File | Purpose |
|---|---|---|
| 📜 Manifest | `configs/ironroot_manifest_data.json` | Declares current_phase + canonical components |
| 📚 File History | `configs/ironroot_file_history_with_dependencies.json` | Tracks per-file phase, deps |
| 🧠 Memory View | `logs/will_memory_log.json` | JSON view of memory events (DB is source of truth) |
| 🔍 Trace View | `logs/reflex_trace_log.json` | JSON view of CLI/reflex traces (DB is source of truth) |
| 📆 Phase Log | `configs/phase_history.json` | Chronological ledger of phases |
| 🧩 Templates | `configs/canonical_templates.md` | Canonical reflex/tool scaffolds |

*Note:* JSON logs are **views**. Persistence is DB-first via `/core/*_db.py`.

---

## 🧭 PHASE LOCKING (MANDATORY)
Every reflex/tool/panel must enforce:
```python
from boot.boot_phase_loader import get_current_phase
if get_current_phase() < REQUIRED_PHASE:
    raise RuntimeError("Phase lock violation")

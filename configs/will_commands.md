# Will Commands — Phase 0.2

✅ **Phase:** 0.2  
🧠 **Codename:** IronSpine_0r

---

## 🧰 CLI Tools

### 🔍 System & Duplication
- `python -m tools.tools_check_dupes`  
  ↪️ Scans all project folders (excluding `__pycache__`, `__init__.py`) for duplicates and misplaced files.

### 🧱 DB Boot & Validation
- `python -m core.sqlite_bootstrap`  
  ↪️ Creates all required tables: `manifest`, `reflex_registry`, `memory_log`, `boot_report`.

- `python -m tools.check_db_tables`  
  ↪️ Lists all tables present in `will_data.db`. Used to confirm bootstrap success.

### 🧪 Lifecycle Test
- `python -m tests.test_phase_0_2_db_lifecycle`  
  ↪️ Inserts + fetches from all core DB tables. Confirms table existence, helper function behavior, and insert/fetch consistency.

---

## 🧪 Reflex Execution
_(No new reflexes registered in 0.2 — this phase focuses on system scaffolding.)_

---

## 📁 Phase 0.2 File References
See:
- `/configs/Phase_02_file_list.json` for list of all Phase 0.2 files
- `/configs/dev_notes.md` for dev history and architectural notes

---

💬 This file maps usable commands and tools after Phase 0.2. It should be updated every time a CLI reflex, test, or utility is added or deprecated.

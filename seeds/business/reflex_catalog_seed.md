
# Reflex Catalog Seed

This document defines and catalogs all active reflexes in Will's system. Each reflex includes its purpose, how it's triggered, what dependencies it requires, and what security level it operates under.

---

## Reflex List

### 🧠 summarize_docs()
- **Purpose**: Reads and summarizes documents for quick understanding.
- **Triggered by**: CLI command or auto-run during ingestion.
- **Dependencies**: `openai`, `document_parser`
- **Security Level**: public

---

### 🗂️ ingest_docs()
- **Purpose**: Ingests all text, PDF, or image files into Will's memory system.
- **Triggered by**: CLI command, auto-watcher (Phase 4+), or GUI drag-and-drop.
- **Dependencies**: `fitz`, `pytesseract`, `PIL`, `sqlite_memory`
- **Security Level**: admin-only

---

### 🧾 pdf_ingest()
- **Purpose**: Detects if a PDF is text- or image-based and extracts content accordingly.
- **Triggered by**: Auto-called by `ingest_docs()` when file is PDF.
- **Dependencies**: `fitz`, `pytesseract`, `PIL`
- **Security Level**: admin-only

---

### 🖼️ image_ingest()
- **Purpose**: OCRs images like `.jpg`, `.png`, etc., and stores extracted text.
- **Triggered by**: Auto-called by `ingest_docs()` or manual CLI.
- **Dependencies**: `pytesseract`, `PIL`, `sqlite_memory`
- **Security Level**: admin-only

---

### 🔍 check_health()
- **Purpose**: Confirms core modules and environment are working.
- **Triggered by**: CLI, GUI diagnostics panel.
- **Dependencies**: internal system checks
- **Security Level**: public

---

### 💾 run_backup()
- **Purpose**: Creates a full backup of Will’s current memory and logs.
- **Triggered by**: Scheduled (cron), CLI, or GUI button.
- **Dependencies**: `sqlite3`, `shutil`, OS-level access
- **Security Level**: system-critical

---

### 📊 report_status()
- **Purpose**: Outputs active projects, memory status, and current task load.
- **Triggered by**: CLI or GUI status widget.
- **Dependencies**: `sqlite_memory`, logging
- **Security Level**: public

---

### 🤔 what_do_I_know()
- **Purpose**: Lists what Will knows about a given project or topic.
- **Triggered by**: CLI, GUI query, or in-chat request.
- **Dependencies**: `sqlite_memory`
- **Security Level**: public

---

## Meta Notes

- **Trigger Methods**
  - `CLI`: Command line script or terminal command
  - `GUI`: Triggered by button or visual interface
  - `Auto`: Triggered automatically by another script or event

- **Security Levels**
  - `public`: Anyone using Will can access
  - `admin-only`: Only trusted users (you) can trigger
  - `system-critical`: Core to backups or restoration

---

## Future-Proof Hooks

- Reflex registry will eventually be loaded dynamically so Will can describe his capabilities without needing manual updates to this file.
- GUI versions will use this catalog to build tooltips, help popups, and visual access controls.

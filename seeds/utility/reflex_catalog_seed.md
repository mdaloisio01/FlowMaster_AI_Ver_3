
# reflex_catalog_seed.md

## Purpose
This file serves as the master registry for all of Will’s reflexes — both core and optional. It provides structure for categorizing, documenting, and tracking every function Will can execute. This seed also lays groundwork for reflex tagging, grouping, and modular loading in the future.

---

## 1. Reflex Structure

Each reflex should follow this standard format:

```json
{
  "name": "reflex_name",
  "category": "system | memory | utility | analysis | input_output | security | business",
  "description": "Brief explanation of what this reflex does",
  "usage": "How and when it’s triggered",
  "dependencies": ["tool_name", "external_api"],
  "fallback_reflex": "optional_alternate_reflex_name",
  "autonomy_level": "manual | semi_auto | full_auto",
  "cli_command": "optional CLI alias"
}
```

---

## 2. Reflex Categories

Will currently supports the following reflex categories:

- **System** – health checks, status reports, backups
- **Memory** – store, retrieve, search, analyze memory
- **Utility** – fallback handling, file ops, transformation
- **Analysis** – error review, code analysis, debug logs
- **Input/Output** – ingest documents, image/OCR, web scraping
- **Security** – encryption, API management, quarantine
- **Business** – task planning, client profiling, branding help

---

## 3. Sample Reflexes

```json
{
  "name": "summarize_docs",
  "category": "input_output",
  "description": "Summarizes uploaded or ingested files",
  "usage": "Triggered after file ingestion",
  "dependencies": ["text_parser", "summarizer_model"],
  "fallback_reflex": "fallback_summarizer",
  "autonomy_level": "full_auto",
  "cli_command": "will summarize --file <name>"
},
{
  "name": "auto_debug_logs",
  "category": "analysis",
  "description": "Analyzes logs and extracts likely error causes",
  "usage": "Runs after failed script or reflex",
  "dependencies": ["log_parser"],
  "fallback_reflex": "manual_review",
  "autonomy_level": "semi_auto"
}
```

---

## 4. Reflex Registry File

Will maintains a local JSON or SQLite reflex registry under:

```
/engine/core/reflex_catalog.json
```

Each reflex is versioned and tagged with install time, update logs, and optional owner metadata for multi-agent systems.

---

## 5. CLI Commands

```bash
will reflex list
will reflex info --name <reflex_name>
will reflex run --name <reflex_name> --args ...
will reflex add --from-file ./my_reflex.py
```

---

## 6. Future-Proofing Features

- **Tags**: Reflexes can be tagged with traits like `#experimental`, `#deprecated`, `#critical`.
- **Version control**: Will tracks version history of reflex updates.
- **Auto-suggestion**: Will suggests useful reflexes based on memory or chat context.
- **Smart loading**: Reflexes not used frequently can be lazily loaded to save memory.
- **Cross-agent sync**: Reflexes can be shared across Will instances (securely).

---

## 7. Reflex Naming Rules

- Use `snake_case` only
- Be descriptive, not vague (`analyze_logs` > `check_it`)
- Avoid reserved keywords

---

## Summary

The reflex catalog is Will’s modular nervous system — every skill he learns, every command he runs, lives here. This seed ensures those reflexes stay:
- Organized
- Extensible
- Secure
- Searchable

It also lays groundwork for smart reflex recommendations and versioning as Will evolves.

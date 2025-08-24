# utility_index_seed.md

## Purpose:
Defines and manages all utility-layer seed files that support Will's reflexes, diagnostics, fallback behaviors, and system tools. Ensures these seeds remain modular, trackable, and scalable as IronRoot evolves.

---

## 🧩 Structure:

Each utility seed file must include:
- `version:` semantic version string (e.g., 1.0.0)
- `used_by:` list of tools or reflexes that depend on this seed
- `checksum:` (auto-generated MD5 or SHA256 hash to verify integrity)
- `overrideable:` [true/false] — if `true`, Will can load override seeds from `/overrides/utility/`

---

## 📄 Utility Seeds:

| Filename                        | Description                                               | Status  |
|--------------------------------|-----------------------------------------------------------|---------|
| fallback_behavior_seed.md      | What to do when things break or fail                     | ✅ Loaded |
| reflex_catalog_seed.md         | Master list of available reflexes + usage metadata       | ✅ Loaded |
| utility_index_seed.md          | (This file) Maps, tracks, and manages utility logic      | ✅ Loaded |
| file_tools_seed.md             | File handling, renaming, safe deletion, compression      | ✅ Loaded |
| terminal_shortcuts_seed.md     | CLI command aliases and hotkeys for faster workflows     | ✅ Loaded |
| module_dependency_seed.md      | Which parts of Will rely on which seeds/tools/modules    | ✅ Loaded |
| path_rules_seed.md             | Default directories, override chains, dynamic fallback   | ✅ Loaded |
| override_priority_seed.md      | How to handle conflicts between core vs override seeds   | ✅ Loaded |
| system_hooks_seed.md           | Triggers for start/stop events, self-checks, error hooks | ✅ Loaded |

---

## 🧠 Smart Self-Improvement Logic

- Will periodically checks:
  - Which utility seeds are underperforming (e.g., fallback triggering too often)
  - Which seeds have checksum mismatches
  - Whether overrides exist and should be promoted to core

- Will may suggest:  
  - Upgrading utility logic  
  - Reviewing unused or stale utility seeds  
  - Archiving overrides that no longer apply  

---

## ⚙️ Override System

If `overrideable: true`, Will checks:
```
/overrides/utility/[seed_name].md
```
...before loading the core seed.

Useful for:
- Client-specific utility logic
- Experimental builds or rapid prototyping
- Partner deployments using white-labeled versions

---

## ✅ Retention and Versioning

- All utility seeds are version-controlled
- Older versions are archived and compared during updates
- Will prefers backward-compatible upgrades unless explicitly told otherwise

---

## Seed Metadata Example:

Each utility seed should start with:

```yaml
version: 1.1.0
used_by: [reflex_engine, error_handler, fallback_manager]
checksum: 9a7b02e1f9c34e1ddfa1a819f3724f72
overrideable: true
```

---

## Notes:

- This index updates automatically during `reflex_catalog_seed.md` reload
- Will not delete any seed — outdated seeds are archived and flagged
- New seeds must be declared here or in a dedicated override index

---

**IronRoot Utility Layer — fast, modular, auditable.**

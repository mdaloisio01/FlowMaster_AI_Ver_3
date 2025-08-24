# plugin_loader_seed.md

## Purpose
This seed defines how Will discovers, loads, verifies, and manages plugins that extend its core functionality. The plugin loader makes Will modular, sandbox-safe, and ready to support hot-swapping new capabilities without restarts or rewrites.

---

## Supported Plugin Types

- ✅ Reflex packs (code tools, extractors, task modules)
- ✅ File handlers (.csv, .html, .pdf, etc.)
- ✅ API wrappers (custom OpenAI endpoints, OCR, web scraping)
- ✅ CLI helpers (subcommands and automation scripts)
- ✅ UI components (for dashboards or alerts)
- ✅ Event triggers (react to uploads, errors, or time schedules)

---

## Loader Behavior

### 🔍 Auto-Discovery
- Recursively scans `/plugins/` and subfolders on startup
- Valid plugin files must contain:
  - `plugin_name`
  - `version`
  - `author`
  - `tags`
  - `autonomy_level`
- Accepts `.py`, `.yaml`, and `.json` formats

### 🧪 Safety & Validation
- Structure check: Ensures required metadata exists
- Fingerprint hash check: Detects tampering or duplicates
- Dependency check: Warns if libraries are missing
- Execution dry-run (optional): Simulates plugin behavior
- Plugin failure = automatic quarantine with log

### ⚙️ Load Strategy
- Load priority:
  1. Core plugins (tag: `core`)
  2. Contextual/project-based (`#flowmaster`, `#benchbot`)
  3. Optional or custom (`#custom`, `#alpha`, `#lab`)
- Can skip or delay plugin loading via:
  - `enabled: false`
  - `load_after_boot: true`

### 🏷️ Tag-Based Loading
Plugins can specify tags for:
- Target project or product (`#ironroot`, `#roaming_raven`)
- Task domain (`#webscraping`, `#3dprinting`, `#analytics`)
- Trust level (`sandbox_only`, `safe_auto`, `full_trust`)
- Execution mode (`background`, `cli`, `api_trigger`)

---

## Autonomy Levels

| Level         | Behavior |
|---------------|----------|
| `sandbox_only` | Cannot run automatically; must be user-invoked |
| `safe_auto`    | Auto-executes when triggered safely (e.g., file upload) |
| `full_trust`   | May run jobs, edit files, or invoke APIs in background |

---

## Future-Proofing Features

- 🔄 **Live Reload**: Reload plugin sets without rebooting Will
- 🧠 **Health Scoring**: Track plugin stability, errors, and uptime
- 🔐 **Security Permissions**: Tag plugins with explicit access rights (e.g., filesystem, subprocess, internet)
- 🧪 **Dry Run Mode**: Simulate plugin runs in safe/no-effect mode
- 📈 **Plugin Feedback Loop**: Log usage frequency, success rate, and execution time
- 🛠️ **Scheduled Jobs**: YAML or tag-defined time-based execution
- 🧾 **Version Locking**: Load specific versions from `plugin.lock` file
- 🌐 **Marketplace Hook**: Support fetching/syncing plugins from Git, S3, or trusted URLs
- 🧬 **Resource Monitor**: Log plugin CPU/memory use
- 🧰 **Plugin Bundles**: Group plugins into importable packs (e.g. `data-cleaning-pack`, `seo-tools`)

---

## Logging & Quarantine

- Invalid or risky plugins moved to `/quarantine/plugins/{plugin_name}/`
- Failure reason logged to `/logs/plugin_failures.log`
- Plugins are NOT retried unless manually cleared or updated

---

## CLI Commands

```bash
will plugins list                 # Show active plugins
will plugin load my_tool.py      # Manually load plugin
will plugin unload analyzer      # Unload plugin by name
will plugin verify               # Check plugin structure + hash
will plugin sandbox foo          # Dry-run plugin in test mode
will plugin healthcheck          # Score plugin performance
will plugin feedback log         # Show usage, failures, and latency
will plugin schedule list        # List registered cron-style jobs
```

---

## Tags
#plugin-loader #sandbox #modular #futureproof #automation #reflex-packs #plugin-health #market-ready

# CLI Command Map Seed

This seed defines Will’s command-line interface behavior. It outlines all supported commands, how they’re grouped, and which flags, environments, tags, and options they support. It also ensures all commands are documented, extensible, and logically organized.

---

## ⚙️ Command Structure Format

Each command entry includes:

```yaml
- name: string
  description: string
  category: string  # e.g., "reflex", "system", "user", "dev"
  usage: string
  flags: [string]
  tags: [string]
  aliases: [string]
  depends_on: [string]
  schedule: string (cron format, optional)
  environments: [string]  # e.g., ["dev", "prod", "offline"]
  interactive: bool
  audit: bool
  help_text:
    en: string
    es: string (optional)
```

---

## 🧭 Sample Commands

```yaml
- name: run_backup
  description: Performs full project and system backup.
  category: system
  usage: will run_backup [--dry-run]
  flags: ["--dry-run", "--force"]
  tags: ["daily", "system", "backup"]
  aliases: ["backup", "bkup"]
  schedule: "0 3 * * *"
  environments: ["dev", "prod"]
  audit: true
  help_text:
    en: "Runs a full system backup. Use --dry-run to preview."
    es: "Ejecuta una copia de seguridad completa. Usa --dry-run para previsualizar."

- name: check_health
  description: Diagnoses system and memory health.
  category: system
  usage: will check_health
  flags: []
  tags: ["diagnostic", "safe"]
  aliases: ["health", "ping"]
  environments: ["dev", "prod", "offline"]
  audit: false
  help_text:
    en: "Checks Will's system health and memory diagnostics."

- name: list_tools
  description: Lists all installed tools and reflexes.
  category: reflex
  usage: will list_tools
  tags: ["tools", "debug"]
  aliases: ["tools"]
  environments: ["dev", "prod"]
  audit: false
  help_text:
    en: "Lists all currently available tools and reflexes."

- name: ask_gpt
  description: Sends a prompt directly to GPT.
  category: dev
  usage: will ask_gpt "your prompt here"
  tags: ["GPT", "prompt", "query"]
  aliases: ["gpt", "chat"]
  environments: ["dev"]
  audit: false
  help_text:
    en: "Sends a direct prompt to GPT and returns the response."
```

---

## ✅ Built-In Enhancements

- **Tags** allow filtered lists and batch operations (`will run @daily`).
- **Aliases** allow short command shorthands or legacy support.
- **Schedules** allow auto-running with the Automation Scheduler.
- **Dependencies** prevent out-of-order execution of linked commands.
- **Environments** restrict command use to proper runtime conditions.
- **Audit** flags commands that should be tracked for history or security logs.
- **Localized Help** prepares for multilingual CLI documentation.
- **Interactive Mode** allows CLI commands to trigger step-by-step workflows.
- **Dry-Run Support** lets you preview destructive commands without executing them.

---

## 🔒 Command Safeguards

- Any destructive or high-impact command must:
  - Be tagged with `@caution` or `@danger`
  - Support `--confirm` or `--force` flags
  - Trigger a confirmation prompt in interactive mode

---

## 🧩 Custom Command Extension

New commands should follow the same YAML format and be injected via `command_hooks` or by editing this seed and regenerating CLI mapping.

---

This seed ensures Will can operate safely, predictably, and flexibly in CLI environments — now and as he grows.


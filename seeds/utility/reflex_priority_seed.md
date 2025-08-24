
# reflex_priority_seed.md

## 🧠 Purpose

This seed defines how Will prioritizes and schedules his reflexes during active operation. It controls what gets done first, what gets deferred, and how Will adapts reflex behavior based on load, project, or your direct commands.

---

## 🧭 Core Principles

- **User-first always**: If Mark gives a prompt or command, all reflexes yield to it. Will waits to resume background work until that request is fully handled.
- **Smart system load balancing**: Will slows, pauses, or reprioritizes reflexes under high system strain.
- **Speed over fluff**: If a reflex isn’t essential, it won’t block or delay more important logic.

---

## 🎯 Default Reflex Priority Tiers

**Tier 1 (Immediate / Always-on)**
- core_behavior_check
- ask_gpt
- memory_index_monitor
- critical_error_watchdog
- chat_input_queue
- system_health_check

**Tier 2 (High)**
- reflex_catalog_update
- enrichment_pipeline
- fastapi_ui_refresh
- backup_scheduler
- ingestion_monitor
- reflex_debugger

**Tier 3 (Standard)**
- reflex_autorun_on_new_files
- archive_old_memory
- keyword_scanner
- web_scrape_watch
- docstring_autowriter

**Tier 4 (Low / Idle-time)**
- cosmetic_ui_updates
- refactor_suggestions
- tag_backfill_engine
- spelling_optimizer
- passive data labeling

---

## ⚙️ Dynamic Reprioritization

Will actively adjusts reflex order based on:

- 🔸 **Active project focus** (IronRoot vs Roaming Raven)
- 🔸 **System CPU/RAM load**
- 🔸 **Manual override via CLI or UI toggle**
- 🔸 **New file or user input arrival**

---

## 🧱 Project-Specific Priority Adjustments

### IronRoot
- Boost: memory strategy, system health, CLI responsiveness
- Suppress: enrichment/autotag unless directly invoked

### FlowMaster
- Boost: UI responsiveness, prompt processing, real-time feedback
- Suppress: backup/archive functions unless idle

### Roaming Raven
- Boost: content enrichment, image parsing, SEO reflexes
- Suppress: internal audit/refactor routines

---

## 🔄 Reflex Dependency Mapping

Will understands dependencies and will never run reflexes out of sequence.  
Example:  
`enrich_file_tags()` waits for `extract_text_from_file()` to complete.

---

## 🧊 Cooldown Timers for Heavy Reflexes

To prevent resource hogging:
- `recursive_file_walk`: 15 sec cooldown
- `batch_web_scrape`: 60 sec cooldown
- `memory_archive_pass`: 5 min idle-only

---

## 🛑 Auto-Yield Logic

Any reflex tagged as `interruptible: true` in its config will yield instantly if:
- A Tier 1 reflex is fired
- A user command is received
- Another higher-priority reflex enters queue

---

## 🎛️ Manual Override Controls

Via CLI, GUI, or future voice:
- `reflex run now <name>`
- `reflex pause <name>`
- `reflex boost <name>`
- `reflex throttle <name>`
- `reflex status`

---

## 🧾 Audit Trail (Reflex Decisions)

Every time Will runs, skips, throttles, or pauses a reflex, the event is logged as:

```json
{
  "reflex": "auto_enrich_files",
  "action": "paused",
  "reason": "user input override",
  "timestamp": "2025-06-27T20:45:00Z"
}
```

These logs are stored in `system/reflex_log.sqlite` and exposed via `reflex report` CLI command.

---

## 🧠 Future Add-ons (Reserved)

- Reflex learning loop: Track what reflexes are often overridden or wasted and retrain order
- Auto-batching similar reflexes for speed boost
- Project-scoped reflex memory to reduce confusion between roles

---

## ✅ Final Notes

Will never sacrifices user responsiveness for background automation.  
If you’re interacting with him, everything else waits.  
If you’re idle, he works like hell in the background — and never forgets his place.


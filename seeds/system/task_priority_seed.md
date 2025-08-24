# task_priority_seed.md

This seed file governs how Will prioritizes tasks, reflexes, and system resources to ensure smooth, responsive, and intelligent behavior under varying load conditions.

---

## 🧠 Core Principles

1. **User Requests First**  
   If the user is actively engaging with Will, that input takes top priority. Will will pause internal tasks to prioritize your prompt or command.

2. **Reflex Autonomy**  
   When not actively being prompted, Will prioritizes reflexes based on urgency, impact, and recent performance data. Reflexes don’t need approval unless flagged as critical or unverified.

3. **Crisis Handling**  
   - If a reflex or task fails, Will retries once using fallback logic.
   - If still unsuccessful, it quarantines the trigger (e.g., bad file, faulty command) and sends a notification.
   - Quarantined items are labeled and isolated for review.

4. **Load-Based Throttling**  
   Will monitors its own workload and deprioritizes non-essential tasks (like cosmetic dashboard updates or background learning) during heavy operations like ingestion, parsing, or indexing.

5. **Latency Awareness**  
   Fast reflexes (<500ms) may be batched or stacked under light load, but throttled during large-scale tasks.

---

## ⚙️ Advanced Task Tuning

### Modular Task Weights

Every reflex/task is scored using four weighted criteria:

- `speed` — how fast it typically completes (lower = better)
- `accuracy` — how reliable the result is
- `frequency` — how often it's used or triggered
- `impact` — how critical it is to core function

Example:
```json
{
  "reflex": "document_ingestion",
  "weights": { "speed": 3, "accuracy": 5, "frequency": 4, "impact": 3 }
}
```

These can be adjusted globally or per-client/project for customization.

---

## 🛡️ Safety Toggles

### Fail-Fast Mode

A config toggle to skip retry/fallback if a task fails the first time — useful in performance-sensitive scenarios.

```bash
--fail-fast=true
```

When enabled:
- Will quarantines immediately on failure.
- Skips diagnostics or secondary parsing.

---

### Real-Time Monitoring Hook

- Reflex execution is tracked in real-time.
- Reflexes that consistently run slow, error out, or spike memory get dynamically deprioritized (unless marked as essential).
- Debug CLI:  
  ```bash
  will reflex-status --live
  ```

---

## 🕵️ Task Shadowing (Future Feature)

When a reflex is deprioritized but likely useful:
- Will simulates first 5 seconds of that reflex in background.
- Results are logged (but not executed).
- This allows learning and adjustment without full activation.

---

## ✅ Deprioritization List (Example)

The following low-priority reflexes are always paused under high load:

- `dashboard_refresh`
- `greeting_generator`
- `auto_summary_weekly`
- `background_cleaning`
- `small_talk_persona`

These can be overridden by config file or CLI.

---

## Feedback Loop

Will logs reflex latency, error rate, and execution volume to constantly adjust its own priorities over time. If a reflex improves performance consistently, it will be promoted higher in the priority tree.

---

## Versioning

- Seed version: `v2.2-fp`
- Last updated: `2025-06-27`

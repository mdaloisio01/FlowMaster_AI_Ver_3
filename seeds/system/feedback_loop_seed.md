# feedback_loop_seed.md

This seed defines how Will evaluates, scores, and learns from his own actions over time — to improve reflex accuracy, speed, and usefulness.

---

## 🎯 Core Purpose

Enable Will to:

- Track success/failure of each reflex
- Learn from outcomes and user input
- Promote helpful reflexes, demote wasteful ones
- Tune suggestions, priorities, and memory relevance based on real usage

---

## 📊 Reflex Performance Scoring

Each reflex logs the following after every run:

- `Execution time`
- `Success/failure`
- `Output length`
- `Follow-up required`
- `User correction/override`

Will builds a running profile for each reflex across sessions.

Example:
```json
{
  "reflex": "summarize_docs",
  "runs": 52,
  "failures": 4,
  "avg_time_ms": 840,
  "corrections": 2
}
```

---

## 🧠 Learning from Memory Context

Will also scores which **memory tags** or data types lead to useful outcomes.

For example:
- “Meeting notes” + “summarize_docs” = high success
- “Screenshot” + “auto_debug_logs” = low success → flag for review

---

## 🚨 Pattern Recognition

If a reflex or task:
- Fails 3+ times in a row
- Regularly exceeds expected time
- Requires user correction more than 20% of the time

…it is **flagged for deprioritization** or sandbox testing.

---

## 🧰 Feedback Tools

### CLI Diagnostics
```bash
will feedback-report --reflex summarize_docs
will reflex-leaderboard --sort=success
```

### GUI Feedback
Will shows reflex scorecards (success %, speed, reliability) in the dashboard or DevView module.

---

## 💬 Optional User Prompts

When enabled:
> “Was this helpful?”  
> [ 👍 Yes ]   [ 👎 No ]

This updates reflex scoring and can be disabled via:
```bash
--no-feedback-prompts
```

---

## 🔄 Automatic Tuning Rules

- Reflexes that rise above 90% success → promoted in priority queue
- Reflexes that drop below 70% → deprioritized, sandboxed, or queued for testing

---

## 📁 Reflex History Store

All scores are saved to:
```
/memory/performance/reflex_scores.db
```
Supports trend analysis, debug snapshots, and long-term tuning.

---

## Versioning

- Seed version: `v1.5-learn`
- Last updated: `2025-06-27`

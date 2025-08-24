# fallback_behavior_seed.md

## Purpose
This file defines how Will handles unexpected failures, unresponsive tools, or missing files. It outlines fallback routines, retry logic, and escalation steps — with flexibility to grow smarter over time and work in tandem with future agents.

---

## 1. Failure Categories

All failures are classified into one of three tiers:

- **Minor (Non-blocking)**  
  UI delays, cosmetic bugs, or small data inconsistencies. Will logs and proceeds.

- **Moderate (Recoverable)**  
  Missing files, API timeouts, or reflex errors. Triggers fallback attempts automatically.

- **Critical (Blocking)**  
  Memory corruption, security risks, or persistent failure. Task halts and Will notifies operator.

---

## 2. Fallback Process

When a failure occurs:

1. **Check for reflex-specific fallback**:  
   If a reflex defines its own `fallback_reflex`, Will uses that first.

2. **Retry Logic (Default)**:  
   - Try original method up to **2 times** (configurable)
   - Wait 3 seconds between attempts
   - If fails, attempt predefined **Plan B method** if one exists
   - If no resolution, proceed to quarantine logic

3. **Quarantine Logic**:  
   - File or task is placed in `/quarantine/`
   - Will tag it with:
     - Failure type
     - Timestamp
     - Attempted methods
     - Any partial results
   - Suggestions are logged to assist with reprocessing or debugging

---

## 3. Memory and Learning

Every fallback attempt is stored with:

- What failed
- The tool/method that failed
- Attempts made
- Outcome
- How long each step took
- Confidence rating

This allows Will to learn over time and adjust his strategy. In future, fallback logs can auto-tune retry strategies based on success rates.

---

## 4. Confidence Thresholds

If fallback attempts result in **< 30% confidence** in the output, Will marks the result as **“Needs Human Review”** and notifies the operator.

---

## 5. CLI Integration

Use these commands to review fallback activity:

```bash
will fallback-log list
will fallback-log details --id <entry_id>
will quarantine list
will quarantine retry --id <file_id>
```

---

## 6. AI Agent Hand-off (Future-Ready)

If a task remains unsolved:
- Will is allowed to **delegate** to compatible AI agents such as:
  - RetrieverBot
  - ScriptFixerDaemon
  - AnalyzerChain
- Task state and fallback history is passed to next agent with full context.

---

## 7. Extensible Reflex Hooks

Each reflex can define optional fields:

```python
{
  "fallback_reflex": "alternate_strategy_name",
  "max_attempts": 3,
  "escalate_if": ["no_response", "timeout", "empty_result"]
}
```

This enables reflex-level customization beyond global rules.

---

## 8. Notes

- All fallback logic respects Will’s system load: low-priority retries are throttled under high CPU or memory usage.
- Archived fallback cases are not deleted unless manually purged.

---

## Summary

Will’s fallback protocol prioritizes:
- Speed (recover quickly)
- Strength (log everything)
- Smoothness (don't crash)
- Future-proofing (gets smarter with age)

This system is designed to adapt as Will scales into more autonomous territory.

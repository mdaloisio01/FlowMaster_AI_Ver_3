# error_categorization_seed.md

### Purpose:
Classifies issues into actionable levels for Will’s self-reporting, reflex adjustments, and escalation tracking.

---

## 🔧 Core Levels

```yaml
error_levels:
  - info:
      description: Non-critical notice; no action needed.
  - warning:
      description: Log it, retry allowed. May indicate degradation.
  - critical:
      description: Triggers reflex pause or requests human input.
```

---

## 🧭 Source Mappings

```yaml
error_source_map:
  - api_timeout: warning
  - json_parse_fail: warning
  - memory_corruption: critical
  - toolchain_missing: critical
  - reflex_not_found: warning
  - unauthorized_access_attempt: critical
  - empty_file_ingest: info
```

---

## 🧩 Modular Error Handlers

```yaml
modular_handlers:
  enabled: true
  override_per_module: true
  task_specific_responses:
    ocr_error: run_reflex("ocr_recovery_mode")
    api_parse_fail: run_reflex("switch_model_or_retry")
    ingestion_error: run_reflex("reingest_with_cleaning")
```

---

## 🔄 Self-Healing Reflex Tracker

```yaml
healing_tracker:
  enabled: true
  store_success_path: true
  link_failed_reflex_to_successful_fix: true
  log_resolution_time: true
```

---

## 🧬 Error Clustering + LLM Commentary

```yaml
cluster_analysis:
  enabled: true
  engine: gpt-4
  group_by: ["stacktrace_hash", "symptom_class", "failure_context"]
  auto_commentary: true
  commentary_prompt: >
    Explain this error in plain English, list likely causes, and recommend 2 fixes.
```

---

## ⏳ Runtime Degradation Detection

```yaml
runtime_health_check:
  enabled: true
  monitor:
    - avg_reflex_time
    - error_rate_per_reflex
    - error_burst_pattern
  trigger_diagnostic_if:
    - error_rate > 10% for > 5 mins
```

---

## 🧰 System Context Snapshots

```yaml
failure_snapshot:
  enabled: true
  includes:
    - open_files
    - reflex_stack
    - active_threads
    - memory_context
    - last_successful_input_output
  retention: 48h
```

---

## 📁 Future-Proofing & Notes

- Add auto-tagging for frequent issues.
- Store error fingerprints and preferred fix paths.
- Auto-prioritize based on frequency and task impact.
- Optional: trigger version drift checks for failed tools.


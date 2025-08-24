# Toolchain Map Seed

This file defines the complete landscape of tools, reflexes, and system functions Will has access to. It allows Will to:

- Understand what tools exist and where to find them
- Check tool status, permissions, and usage guidelines
- Map and execute tools as workflows
- Autonomously prioritize, validate, or chain tool calls

---

## 🔧 Tool Entry Format

Each tool should be defined with the following metadata:

```yaml
- name: "summarize_docs"
  category: "reflex"
  description: "Summarizes uploaded documents and stores core insights."
  entrypoint: "reflexes/summarize_docs.py::summarize_docs"
  dependencies: ["document_ingestion", "memory_write"]
  example_usage: "Will, summarize the project notes from yesterday."
  version: "1.2.0"
  status: "active" # options: active, experimental, deprecated, broken
  execution_tags: ["safe_to_run_autonomously", "read_only"]
  access_level_required: "user"
  average_runtime: "3s"
```

---

## ✅ Execution Tags Reference

- `safe_to_run_autonomously`: No approval required
- `requires_human_confirmation`: Ask before execution
- `long_execution_time`: Flag for planning/scheduling
- `read_only`: No permanent changes made
- `write_to_memory`: Tool affects Will’s long-term memory
- `external_dependency`: May rely on external APIs

---

## 📦 Tool Categories

- **reflex**: Smart AI behaviors triggered via voice/chat command
- **cli**: Terminal-level scripts or admin commands
- **system**: Will’s internal management/diagnostics tools
- **external**: Web scrapers, API calls, plugin runners

---

## 🔁 Toolchain Recipes

Define workflows Will can execute as chains:

```yaml
- name: "insight_response_flow"
  steps:
    - "summarize_docs"
    - "analyze_sentiment"
    - "store_summary"
  description: "Used when a user uploads a doc and wants summarized memory + insights"
```

---

## 🔒 Security & Access Levels

Tools can be restricted by these access levels:

- `system`: Only Will or a root process can run
- `admin`: Developer or internal use only
- `user`: Available during normal Will chat
- `guest`: Safe for client-facing use

---

## ⚙️ Auto-Update Reflex

Reflex: `update_toolchain_map(force=False)`

- Automatically refreshes this map based on file inspection
- Detects added, removed, or broken tools
- Logs tool changes in system memory
- Skips updates for tools marked `manual_control: true`

---

## 📅 Roadmap Section (Optional)

You may also define tools that don’t exist *yet*, but are planned:

```yaml
- name: "predict_profit_curve"
  status: "planned"
  priority: "medium"
  description: "Forecasts income trends based on client data"
  dependencies: ["financial_modeling", "historical_sales"]
```

---

## 🧠 Load-Aware Behavior

Will uses the following logic:

- Track average run time per tool
- Favor `read_only` and low-runtime tools when under load
- Log any high-latency tools for performance tuning

---

## 💥 Compatibility Matrix (Optional per tool)

Track versions, language support, or OS requirements:

```yaml
- name: "scrape_web_data"
  compatible:
    python: ">=3.10"
    modules: ["requests", "beautifulsoup4"]
    notes: "Fails under SQLite memory mode due to missing parser"
```

---

## 🛡️ Future-Ready Features

- Tools marked as `deprecated` trigger an alert before running
- Tools with missing dependencies are auto-disabled and flagged
- Will includes these tool stats in self-diagnostic reports
- Version drift warnings included when tools don’t match core runtime

---

End of file.

# custom_parser_seed.md

## Purpose:
Handles extraction from unusual, messy, or domain-specific formats that don’t cleanly fit Will’s default ingestion pipeline.

---

## Supported Custom File Types:
```yaml
known_custom_types:
  - .log
  - .ini
  - .conf
  - .csv
  - .jsonl
  - .dat
  - .bak
  - .tmp.log
```

---

## Parsing Rules by Type:
```yaml
parsing_strategies:
  .log:
    strategy: regex
    output_format: structured_json
    normalize_timestamps: ISO
    reflex: parse_logs
  .ini:
    strategy: key_value_pairs
    output_format: json
    reflex: parse_config_files
  .csv:
    strategy: delimiter_split
    output_format: dataframe
    reflex: parse_csv_flex
  .jsonl:
    strategy: line_by_line_json
    output_format: list[dict]
    reflex: parse_jsonl
```

---

## Multi-Pass Parsing:
```yaml
multi_pass:
  enabled: true
  steps:
    - pre_clean
    - detect_schema
    - parse_and_validate
    - normalize
```

---

## Parser Confidence Scoring:
```yaml
parser_confidence:
  enabled: true
  threshold_pass: 90
  threshold_warn: 70
  threshold_fail: 50
  auto_log_low_confidence: true
```

---

## Quarantine & Fallback Handling:
```yaml
fallback_parser:
  reflex: generic_fallback_parser
  quarantine_on_fail: true
  quarantine_path: /quarantine/unreadable_files/
  auto_notify: true
```

---

## Data Sensitivity Flags:
```yaml
sensitivity_flags:
  - file_types: [.csv, .xlsx, .ehr]
    scan_for: [ssn, email, phone_number]
    redact_before_storage: true
    require_encryption: true
```

---

## Feedback Loop for Unknown Formats:
```yaml
feedback_loop:
  unknown_file_type:
    actions:
      - snapshot_sample
      - extract_header_lines
      - log_error
      - store_in: /training/parsers/new_cases/
      - flag_for_review: true
```

---

## Plugin Support:
```yaml
custom_plugins:
  enabled: true
  plugin_paths:
    - /plugins/parsers/
    - /client_overrides/custom_parsers/
```

---

## Future-proofing Extras:
- ✅ Wildcard extension support (`*.bak`, `*.tmp.log`)
- ✅ Client-format memory: remembers how to parse files per client
- ✅ Cross-platform: normalize newline characters across OS
- ✅ Auto-suggest: Will proposes parser improvements after 3+ similar failures

---

Let me know if you'd like to link this parser to ingestion memory tracking or tagging — we can embed that too 👊

# task_template_seed.md

### Purpose:
Define reusable, modular, and smart action pipelines that Will can execute across different workflows.

---

## 🔧 Structure:

Each task template includes:

- `template_id`: Unique name for reference
- `description`: Purpose of the task
- `reflexes`: Ordered list of reflexes used
- `input_format`: Required input types
- `output_format`: What is produced
- `resource_limits`: (Optional) Timeouts, file size caps
- `memory_tags`: Contextual tags to add during run
- `schedule`: Optional trigger details
- `output_routing`: Where to send/save results
- `group_id`: Optional collection grouping
- `extends`: Template inheritance

---

## 📁 Templates:

```yaml
- template_id: analyze_site_seo
  description: Crawl a site, analyze keywords, and export as CSV
  reflexes:
    - crawl_site
    - analyze_keywords
    - export_csv
  input_format: url
  output_format: csv
  resource_limits:
    timeout: 60s
  memory_tags:
    - #seo
    - #site_analysis
  schedule:
    cron: "0 9 * * MON"
  output_routing:
    save_to: /reports/seo/
    notify: slack:webhooks/seo-alert
  group_id: marketing_workflows

- template_id: summarize_emails
  description: Ingest emails and summarize key points
  reflexes:
    - ingest_emails
    - detect_leads
    - summarize_thread
  input_format: .eml, .txt
  output_format: .md
  memory_tags:
    - #client_comm
  output_routing:
    append_to_memory: true
  schedule:
    on_event: new_email_received

- template_id: advanced_ocr_pipeline
  description: Convert image or PDF to searchable text, normalize, and store
  reflexes:
    - convert_image
    - extract_text
    - normalize_text
    - save_to_pdf
  input_format: .jpg, .png, .pdf
  output_format: .pdf
  resource_limits:
    file_size_max: 25MB
  output_routing:
    save_to: /docs/ocr/
    notify: dashboard
  memory_tags:
    - #ocr
    - #doc_ingestion
```

---

## 🧬 Inheritance Example

```yaml
- template_id: custom_client_onboarding
  extends: analyze_site_seo
  override:
    reflexes[2]: send_intro_email
    output_routing.save_to: /onboarding_reports/
```

---

## 🛠 GUI Enhancements (Optional Visual Builder Support)

```yaml
- template_id: upload_contract_and_tag
  step_name: Upload → Extract → Memory
  icon: 📄
  color: blue
  input_form:
    file: upload
    client_name: text
    urgency: dropdown[low, medium, high]
```

---

## 🧠 Reflex Swap (Advanced Logic)

Will may dynamically select reflex versions based on:

- Input type/quality
- API key availability
- Cost/latency optimization
- Backup/failover logic

---

## Future-Proof Notes:

- ✅ Supports drag-and-drop UI design
- ✅ Pre-annotates memory with topic and context
- ✅ Output routing integrates with notification reflexes
- ✅ Enables full automation without coding
- ✅ Grouping allows bundled workflows per department or use case

---

Let me know if you want to pre-populate some grouped bundles for common use cases (e.g., lead gen, legal review, onboarding) — I can build a starter pack. Ready for next seed when you are 👊


# workflow_templates_seed.md

## Purpose:
This seed defines how workflow templates are created, structured, categorized, secured, and improved over time. These templates power many of Will’s automated operations, including reflex chaining, system diagnostics, onboarding, and multi-step task execution.

---

## 🧠 What Is a Workflow Template?

A workflow template is a modular, reusable YAML or JSON structure that defines:

- Steps to perform (in order)
- Optional triggers or conditions
- Input/output expectations
- Reflexes or system tools used
- Roles/permissions required to run
- Hooks or logic for start/end
- Version history and rollback options

Templates let Will adapt, scale, and perform autonomous actions across different areas like diagnostics, support, data ingestion, and scheduling.

---

## 🔧 Template Format (YAML)

```yaml
id: client_onboarding_standard
version: 2.1
description: Onboards a new client into IronRoot systems.
tags:
  - onboarding
  - client_ops

required_role: admin
confirm_before_run: true

dependencies:
  - verify_business_entity
  - setup_crm_profile

steps:
  - collect_client_info
  - create_workspace
  - setup_initial_tools
  - send_welcome_email

pre_hooks:
  - log_input_parameters

post_hooks:
  - notify_internal_team
  - archive_workflow_run
```

---

## 📂 Directory Structure

```
/workflows/
├── templates/
│   ├── client_onboarding_standard.yaml
│   ├── diagnostics_full_sweep.yaml
│   └── [others...]
│
├── _archive/
│   ├── deprecated_client_onboarding_v1.yaml
│   └── test_sequence_v0.9.yaml
```

- All active templates live in `/workflows/templates/`
- Old versions or retired flows are moved to `/workflows/_archive/`

---

## 🔐 Permissions & Security

Will checks:

- `required_role:` before running
- If `confirm_before_run: true`, user must approve before launch
- Any injected steps from external triggers must be tagged safe or explicitly authorized

---

## ⚙️ Runtime Enhancements

- Templates support **dynamic step injection** (from reflexes or CLI)
- **Event hooks** allow logging, validation, or notifications before/after execution
- **Tags** allow smart filtering, prioritization, and interface grouping

---

## 📊 Optimization Reflex (Future)

Reflex: `optimize_workflow(template_id)`

Will will use past run data, step timing, errors, and user feedback to:

- Suggest faster/fewer steps
- Identify unnecessary logic
- Highlight failure points
- Auto-suggest retry strategies

---

## ✅ Best Practices

- Every new automation should be built from a reusable template
- Use semantic versioning (`1.0`, `2.1`) and changelogs
- Add `tags:` for searchability and dashboards
- Archive templates instead of deleting them

---

## 🔄 Maintenance

- Templates should be reviewed quarterly
- Deprecated workflows go to `_archive/`
- If workflows are client-visible, include branded messaging steps (via `post_hooks`)

---

## 📌 CLI Example

```
will run_workflow client_onboarding_standard --force
will list_workflows --tag onboarding
will optimize_workflow client_onboarding_standard
```

---

## 🔮 Future Upgrades (Planned Reflexes)

- `suggest_workflow(user_input)` — Will proposes a template based on user goals
- `convert_chat_to_workflow()` — Create new workflow templates from natural conversations

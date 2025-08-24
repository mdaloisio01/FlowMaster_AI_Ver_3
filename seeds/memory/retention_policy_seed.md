✅ Final Version: retention_policy_seed.md

# Retention Policy Seed
Defines how Will handles memory over time — for live use, archiving, and long-term storage.

---

## 🔹 Core Rules

- ❌ **No memory is ever deleted.**
  - This includes failed attempts, bad OCR, or even nonsense — if it was ingested, it's saved.
  - “Archiving” is allowed. “Erasing” is not.

- 🧠 **Live memory stays lean.**
  - Will prioritizes *active*, recently used, or tagged memory when querying.
  - Background queries will search both live and archived memory when needed.

---

## 🗃️ Archiving Logic

- Memory older than **90 days** moves to archive unless tagged `pinned` or `essential`.
- Archived items can still be queried and restored automatically if relevant.
- You can “pin” important entries to avoid archive.
  
```yaml
archive_threshold_days: 90
pinned_tags: [pinned, essential]
🛑 Legal Hold & Overrides
If legal_hold = true, memory is locked — no archiving, no hiding, no changes.

Clients/projects can define custom archive rules in the project index or seed.


SystemFlags:
  legal_hold: false
RetentionOverrides:
  IronRoot:
    archive_threshold_days: 120
    pinned_tags: [audit, compliance]
🔍 Search Visibility
Sensitive content can be suppressed from normal queries:


searchable: false
tags: [api_key, private_log]
🗓️ Review Triggers
Will can tag memory with review_on dates to prompt future follow-up:

review_on: 2025-09-01
🧾 Retention Audit Reflex
Will runs regular audits to:

List items nearing archive

Flag anything with suppressed visibility

Recommend pinned upgrades for core ops

---

Let me know if you want a GUI panel later to manage this stuff or tweak project-specific rules. Otherwise, this one’s ready to lock in. Want to save it and move on to the next seed?







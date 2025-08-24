naming_conventions_seed.md
📂 Location: /seeds/memory/naming_conventions_seed.md
🧠 Purpose: Define consistent, machine-friendly, human-readable naming rules for all files, folders, tags, and memory entries across the Will/IronRoot ecosystem.

🔹 General Principles
Names must be clear, scalable, and automatable.

All naming must support:

Cross-platform compatibility (Windows/macOS/Linux).

Easy sorting (alphabetical, chronological).

Script-friendly automation.

🔸 FILE NAMING
✅ Format:
php-template
Copy
Edit
<project>_<topic>_<tag1>-<tag2>_YYYY-MM-DD[_vX].ext
Example:
ironroot_memory_indexing_search-vs-indexing_2025-06-27_v1.md

✅ Rules:
Rule	Reason
Use kebab-case for words in filenames	Easy to read + script safe
Use _underscores_ to separate sections	Cleaner parsing
Add date in YYYY-MM-DD format	Easy sorting & backups
Use optional _v# suffix for versions	Tracks iterations
Use lowercase only	Prevents OS conflicts

🔸 MEMORY ENTRY KEYS
✅ Format:
nginx
Copy
Edit
project_topic_tag1_tag2_timestamp
Example:
ironroot_memory_ingestion_rules_data-cleaning_2025-06-27_1542

✅ Rules:
Rule	Reason
Use snake_case for memory keys	Preferred in code/DB
Timestamp format: YYYY-MM-DD_HHMM	Unique + sortable
Avoid long tag chains (>4 tags)	Keep concise & fast to index
No special characters	Prevent DB or JSON errors

🔸 TAG RULES
✅ Always lowercase

✅ Multi-word tags must use hyphens: data-cleaning, not DataCleaning

🚫 No spaces, underscores, or punctuation

🔢 Limit to 3 words per tag

❗ If multi-brand, prefix tags: ironroot-ingestion, raven-travel

🔸 VERSIONING
Files that evolve should include _v1, _v2, etc.

Will will eventually:

Auto-version based on changes

Archive old versions

Track changelog diffs in memory

🔸 RESERVED / FORBIDDEN NAMES
Will will warn or reject:

final, temp, new, copy, untitled, do_not_delete, test

These cause confusion or automation conflicts

🔸 NAMESPACE AWARENESS
If Will serves multiple brands/projects:

Always prefix with brand:

ironroot_, flowmaster_, roamingraven_, etc.

Applies to:

Filenames

Tags

Memory keys

Seed files

🔸 Notes for Future-Proofing
✅ All rules support future upgrades like:

Smart indexing

Dynamic search

Memory diffing/version control

Automated training and ingestion pipelines


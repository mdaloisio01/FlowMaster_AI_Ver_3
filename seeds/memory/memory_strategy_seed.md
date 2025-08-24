memory_strategy_seed.md
Purpose:
This file defines how Will handles memory — what he remembers, how long, what matters most, and how to deal with conflicts or noise. The goal is to keep Will fast, smart, scalable, and organized.

🔹 Memory Core Principles
Speed first, clarity always – Fast access to important memories with context clarity.

Futureproofed – System must scale across projects, users, and versions.

Minimal waste – Avoid redundant or dead-end memory buildup.

🧠 Memory Structure
All entries are timestamped, categorized by:

project

topic

tags

content

Stored in SQLite for fast, local, low-bloat operation (can scale to cloud later).

Full-text searchable.

Relationships between entries allowed via tags and topic threading.

⏳ Memory Aging & Expiry
Default memory lifespan: Permanent unless archived or replaced.

Auto-archiving rules:

Logs older than 90 days = archive unless flagged as critical.

Deprecated seeds or phases = archive when next version is confirmed.

Fade behavior: Non-referenced logs >120 days are marked for low-priority recall.

⚖️ Context Weighting
Each memory gets a context score (1–10 scale):

Score increases when:

Topic is revisited

Entry is referenced by Will or user

Score decreases when:

Entry is old and unused

Entry is marked as deprecated

Critical systems (reflexes, core plans) always maintain high priority

🔁 Redundancy & Conflict Strategy
If duplicate content is detected:

Keep the latest version

Link older version as “historical”

If two entries directly conflict:

Will tries to infer correct version by:

Timestamp relevance

Confirmation from the latest plan

If unsure, Will flags it to the user (with context preview)

🧩 Memory Relationships & Linking
Related memories are tagged together

e.g. reflex:auto_debug_logs is linked to project:IronRoot and phase_map_seed

Will builds internal maps of linked data for fast recall and decision-making

👤 User Zones (Planned for Future Multi-User Support)
Memory is partitioned by:

user_id

project_id

Shared memory: reflex code, public seeds, platform-wide logs

Private memory: user-specific logs, custom behaviors, preferences

🧽 Preprocessing / Clean-up
Will stores both:

raw_input: Original content (for audit/debug)

cleaned_content: Parsed, trimmed, normalized version

This ensures reversibility without sacrificing speed or data hygiene

🧠 Minimum Text Threshold
No minimum word limit — if a user uploads a file with just “hello world,” Will keeps it. If they thought it mattered, that’s good enough.

End of file
This seed ensures Will’s memory remains fast, accurate, conflict-aware, and ready to scale with you or your clients.


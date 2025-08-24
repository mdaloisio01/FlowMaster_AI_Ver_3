🧠 memory_indexing_seed.md
Purpose
This seed defines how Will should organize and interact with memory. Its goal is to keep memory fast, relevant, structured, and scale-ready across different projects, topics, and data sources.

📌 Core Indexing Structure
All memory should be indexed using the following fields:

project: The high-level initiative or business unit (e.g. IronRoot, Roaming Raven).

topic: A specific subject or feature inside the project (e.g. dashboard_ui, branding_rules).

tags: Optional keywords to help with sorting, filtering, or cross-project linking.

timestamp: Stored in UTC, used for sorting and relevance scoring.

source_type: What type of input generated this memory? (user_input, pdf, image_ocr, log_event, etc.)

content: The actual extracted, typed, or generated text.

✅ This ensures Will can handle diverse file types, user commands, and internal events with a consistent structure.

🧮 Relevance Tracking
Will should apply a memory relevance score based on:

How recently it was accessed

How often it's referenced or re-tagged

Whether it’s flagged as #permanent or #temp

This allows for intelligent memory decay and priority highlighting without full deletion.

🧹 Retention Rules
These rules determine when and how old or unused memory is cleaned up:

Tag or Type	Rule
#temp	Auto-purge after 7 days
Unused memory	Auto-archive after 90 days
#permanent	Never delete unless manually flagged
system_logs	Archive after 30 days

Will should respect these without manual prompts unless configured otherwise.

🔍 Natural Language Search (Future Phase)
Will should eventually be able to:

Search memory using full-text queries

Parse natural language like:

“What did we say about dashboard launch?”

Return results sorted by relevance + freshness

Supports scaling up to long-term memory search for teams, clients, or multi-phase projects.

🔄 Cross-Project Linking
Will should detect and suggest related memory across projects if:

Shared tags exist (like #dashboard, #deployment)

The topics are semantically linked

Reused templates or workflows exist

Example:

Branding guidance from IronRoot might help FlowMaster UI decisions. Will should highlight that.

📁 Multi-format Input Ready
Will is expected to handle and correctly index memory from:

.txt, .md, .pdf, .jpg, .png, .docx, .csv, .html

OCR results

Scraped web content (via source_type: web_scrape)

Human input (chat or GUI forms)

This ensures consistent memory quality no matter how info enters the system.

💡 Final Notes
Memory indexing is foundational. If this structure fails, everything else breaks.

Will should always favor precision, clarity, and speed when accessing memory.

He should never “guess” if uncertain — fallback to prompting the user or flagging the memory for review.
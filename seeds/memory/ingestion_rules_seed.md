ingestion_rules_seed.md
Purpose:
Defines how Will should handle and process all incoming files, across every supported format, while staying efficient, clean, and future-proof.

🔍 File Type Support
Will should accept and process the following formats:

.txt, .md (plain/markdown text)

.pdf (text-based and image-based with OCR fallback)

.jpg, .png, .jpeg (OCR with Tesseract)

.docx, .csv, .html (structured text formats)

❌ Files like .exe, .bat, .sh, and archives (.zip, .rar) are blocked by default.

🧠 Ingestion Workflow
Determine File Type

Automatically detect file extension

Route to proper handler (text, OCR, docx, etc.)

Try Primary Ingestion

Use the cleanest, most direct method first (e.g., built-in PDF text, CSV reader)

Fallback if Needed

If primary fails, use fallback (e.g., OCR for images or failed PDFs)

Store Both Raw & Clean (if applicable)

Raw version: original untouched contents

Clean version: trimmed of junk, normalized spacing, cleaned up encoding

⚠️ If needed, the system can refer back to the raw version for reprocessing.

Quarantine on Final Failure

If a file fully fails after fallback, Will:

Flags the issue

Moves file to quarantine/ folder

Logs the issue and sends notification

🏷️ Project/Topic/Tags
Primary Method:
Parse the filename using the format:
project_topic_tag1_tag2_tag3.ext

Override Options:
Look for file header metadata (#project:FlowMaster)

Check embedded metadata (PDF title, EXIF, etc.)

🧠 Minimum Text Threshold
Will stores everything, no matter how small — even a file with just “hello world.”
Assumes if the user uploaded it, it matters.

🔄 Re-ingestion & Versioning
Will track each file’s content hash.

If a file is re-uploaded:

✅ New content → reprocess and overwrite

❌ Duplicate content → skip and log as duplicate

💬 Auto-Tagging Assistance
If filename is vague or missing tags, Will:

Parses the content for high-frequency keywords

Suggests probable tags based on past data

Tags with “#untagged” if unsure

🌍 Language Detection (Prep for Multilingual Use)
Detects document language

Adds #lang:<code> to metadata

Flags for future translation module (Phase 6+)

⚠️ Basic File Safety
Block dangerous or non-textual formats

Run basic threat scan on plaintext (look for obfuscation or injection)

No scriptable input allowed for ingestion

🕓 Timestamps & Audit Trail
Every file gets a full ingest log including:

created_at: original file creation date

uploaded_at: when user dropped file in

processed_at: when Will ingested it

status: success, fallback, quarantine
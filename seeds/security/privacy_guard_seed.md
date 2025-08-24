🧪 Reflex Sandbox Seed
🧠 What Is It?
The Reflex Sandbox is Will’s safe zone for testing new reflexes before they’re trusted with real memory, tools, or access to sensitive systems.

New reflexes always start here, unless manually promoted with elevated rights.

🔐 Sandbox Execution Rules
1. Reflexes run in an isolated test mode
Can’t modify main_memory.sqlite

Can’t touch project folders outside /sandbox/

Can’t make real API calls (unless override flag enabled)

2. Must be tagged to run
All reflexes must include:

status = {
    "sandbox": True,
    "verified": False,
    "dangerous": False
}
Missing tags = will not run.

3. Logs every run
Each sandbox reflex logs into:

/reflexes/sandbox/logs/reflex_run_log.json
Includes:

Timestamp

Inputs

Output

Runtime

Errors

Auto-score update

✅ CLI Tool: Promote Reflex
A command-line utility for moving a reflex out of the sandbox and into verified mode.

📦 Command

python cli/promote_reflex.py test_scraper_alpha.py
🔧 What it does:
Moves the file:

From /reflexes/sandbox/ → /reflexes/verified/

Updates the file’s metadata:

Changes status["sandbox"] to False

Sets status["verified"] to True

Assigns a version = "1.0.0" if not already set

Records in:

/reflexes/changelog.json

/reflexes/trust_scores.json

(Optional) Notifies admin via dashboard or email

🛡️ Safety Bumpers While Sandboxed
Reflex memory writes go to: sandbox_memory.sqlite

File saves go to: /sandbox/

Internet access: blocked unless ALLOW_EXTERNAL=True

System commands like os.system() are blocked

Fail-safe: After 3 consecutive failures, reflex is auto-moved to /quarantine/

📊 Trust Score System
Each reflex earns a trust score from 0–100:

+10 per successful run

−25 for each crash or major error

+5 if user manually rates/refines it

+15 on verified promotion

Used to sort or auto-deprioritize sketchy code.

🧾 Changelog Tracking
Each promoted reflex adds an entry:


{
  "reflex": "test_scraper_alpha.py",
  "promoted_on": "2025-06-26",
  "version": "1.0.0",
  "summary": "Initial promotion from sandbox to verified.",
  "author": "admin"
}
Helps keep track of what’s been added or changed.

🧬 Futureproofing Enhancements
✅ Add test harness for sandbox reflexes using pytest

✅ Create GUI toggle to mark reflexes as verified or quarantine

✅ Auto-generate docstring summary when promoted

🔖 Folder Layout

/reflexes/
│
├── sandbox/
│   ├── test_scraper_alpha.py
│   ├── logs/
│   │   └── reflex_run_log.json
│   └── quarantine/
│       └── broken_reflex.py
│
├── verified/
│   ├── summarize_docs.py
│   └── ingest_docs.py
│
├── trust_scores.json
├── changelog.json
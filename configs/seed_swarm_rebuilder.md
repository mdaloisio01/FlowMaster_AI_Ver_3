🔷 SWARM REBUILDER SEED — IronSpine-Compliant Agentic Swarm for Codebase Healing



❗ Required Phase ≥ 0.3 (trace layer)  

REQUIRED\_PHASE = 0.3



---



\## OVERARCHING PURPOSE

Take an existing codebase (e.g. Will v1), chunk its files, and iteratively audit + refactor them into IronRoot-compliant form via a swarm of agents, all fully traceable, phase-locked, and safe.



---



\## AGENT ROLES



\### \*\*auditor\_reflex.py\*\*

\- Phase-locked at REQUIRED\_PHASE  

\- Reads a file chunk  

\- Detects violations (phase drift, ghost logic, missing dual logs)  

\- Returns structured audit JSON (file, issues, severity)



\### \*\*rebuilder\_reflex.py\*\*

\- Phase-locked  

\- Accepts audit + chunk  

\- Rewrites full file (or chunk) to comply  

\- Registers in manifest history if new  

\- Emits patch or full file rewrite, with dual logging



\### \*\*reviewer\_reflex.py\*\*

\- Phase-locked  

\- Compares original + patch + audit  

\- Validates compliance: phase lock present, dual logs, no regression  

\- Approves or rejects patch



\### \*\*github\_integration\_reflex.py\*\*

\- Phase-locked  

\- Takes approved patch  

\- Creates GitHub branch / PR (never write to main)  

\- Sync-check: do not override unmerged concurrent changes  

\- Dual logs commit metadata



\### \*\*orchestrator.py\*\*

\- Manages loop: chunk selection → auditor → rebuilder → reviewer → github commit  

\- Tracks iteration limits, rollbacks  

\- Enforces fail-safes (if reviewer rejects repeatedly, halt)  

\- Powers the swarm coordination



---



\## CHUNK STORAGE \& INDEX



\- `chunk\_store.db` (SQLite) with table:  

&nbsp; ```sql

&nbsp; chunks (

&nbsp;   id INTEGER PRIMARY KEY,

&nbsp;   file\_path TEXT,

&nbsp;   chunk\_index INTEGER,

&nbsp;   chunk\_hash TEXT,

&nbsp;   summary TEXT,

&nbsp;   status TEXT,            -- "pending", "audited", "rebuilt", "approved"

&nbsp;   original\_hash TEXT,

&nbsp;   created\_at TIMESTAMP

&nbsp; );




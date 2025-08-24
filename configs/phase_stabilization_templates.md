0) How to use this recipe book (simple)
Pick the template you need (seed file, reflex, CLI tool, test, manifest entry, etc.).

Copy it verbatim and fill in the placeholders only (names, phase numbers, brief purpose).

After generating files, run your Phase 0 tools:

python -m tools.update_phase_tracking

python -m tools.trace_inspector --tag <your_tag>

python -m tools.verify_log_integrity

python -m tools.reflex_compliance_guard (Phase ≥ 0.4)

If any check fails, stop and fix it. Do not continue.

1) Phase Seed File — Canonical Template
(Use this to start any phase. Paste into /configs/Phase_XX_Seed_File.md)

# PHASE SEED — Phase <X.Y>: <Codename>
Build Type: IronSpine Skeleton
Governed By: IronRoot Law v1.0
Status: ✅ Ready for Build

🎯 Objective
<One paragraph: what this phase locks in and why>

📁 Files To Build/Modify (alpha order)
- /core/<...>.py — <purpose>
- /reflexes/reflex_core/<...>.py — <purpose>
- /tools/<...>.py — <purpose>
- /tests/<...>.py — <purpose>
- /configs/<...>.md|json — <purpose>
- /logs/<...>.json — <purpose>

🧪 Required Tests
- Command(s):  
  - python -m tools.update_phase_tracking  
  - python -m tests.<file>  
  - python -m tools.trace_inspector --tag <tag>  
  - python -m tools.verify_log_integrity

🔐 Enforcement Rules
- All files must be in manifest + file history
- All modules phase‑locked via get_current_phase()
- Every reflex/tool dual‑logs (memory + trace)
- Full files only; no patches or stubs without logging

🚨 Failure Policy
If any check fails:  
`🚨 IRONROOT VIOLATION — <reason>. <full path>. Build cannot proceed.`

📌 Exit Criteria (all must pass)
- Build + tests green
- Dual logging verified
- Manifest + history updated
- Phase stamped into phase_history.json + build_log.json

2) Manifest & File‑History update snippets
(Use these blocks when updating JSON; keep keys in alpha order.)
/configs/ironroot_manifest_data.json (fragment)

{
  "current_phase": <X.Y>,
  "manifest": {
    "configs": [
      "configs/Phase_<X_Y>_Seed_File.md",
      "configs/dev_bot_bootstrap.md",
      "configs/ironroot_manifest_data.json",
      "configs/ironroot_file_history_with_dependencies.json",
      "configs/phase_history.json",
      "configs/dev_file_list.md",
      "configs/will_commands.md"
    ],
    "core": [
      "core/sqlite_bootstrap.py",
      "core/trace_logger.py",
      "<add new core files here>"
    ],
    "reflexes": [
      "reflexes/reflex_core/reflex_trace_ping.py",
      "<add new reflexes here>"
    ],
    "tools": [
      "tools/will_cli.py",
      "tools/trace_inspector.py",
      "tools/update_phase_tracking.py",
      "<add new tools here>"
    ],
    "tests": [
      "tests/test_phase_0_integrity.py",
      "<add new tests here>"
    ],
    "logs": [
      "logs/boot_trace_log.json",
      "logs/reflex_trace_log.json",
      "logs/will_memory_log.json"
    ],
    "sandbox": [
      "sandbox/sandbox_reflex_tests.py"
    ],
    "root": [
      "test.json",
      "will_data.db"
    ]
  }
}


/configs/ironroot_file_history_with_dependencies.json (fragment)

{
  "history": {
    "core/trace_logger.py": { "phase": 0.3 },
    "tools/trace_inspector.py": { "phase": 0.3 },
    "tools/reflex_compliance_guard.py": { "phase": 0.4 },
    "<new_path>": { "phase": <X.Y> }
  }
}


3) Phase bookkeeping — build & history entries
/configs/build_log.json — append pattern

{
  "phase": <X.Y>,
  "codename": "<Codename>",
  "status": "✅ Completed",
  "validated_on": "<ISO-8601 UTC>",
  "tests_passed": [
    "<test files or tool names>"
  ],
  "reflexes_tested": ["<names>"],
  "cli_tools_tested": ["<names>"],
  "memory_trace": "✅ Active and logging",
  "notes": "<brief what changed and why>"
}

/configs/phase_history.json — entry

{
  "phase": <X.Y>,
  "status": "✅ Complete",
  "timestamp": "<ISO-8601 with TZ>",
  "description": "<one-line summary>"
}


4) Canonical Reflex Template (Drop‑In Scaffold)
(Already in your canonical_templates.md; duplicated here to keep the book single‑file complete.)

# /reflexes/reflex_core/<your_reflex_name>.py
"""
Reflex: <your_reflex_name>
Phase: <REQUIRED_PHASE_INT>
Purpose: <one-line purpose>
"""

from boot.boot_path_initializer import inject_paths
inject_paths()

from configs.ironroot_manifest_loader import get_current_phase
from core.memory_log_db import log_memory_event
from core.trace_logger import log_trace_event

REQUIRED_PHASE = <REQUIRED_PHASE_INT>

def run(**kwargs):
    if get_current_phase() < REQUIRED_PHASE:
        raise RuntimeError("❌ Not allowed in this phase")

    result = {"status": "ok", "details": "replace with real logic"}

    log_memory_event(
        event_type="reflex_run",
        phase=REQUIRED_PHASE,
        source=__name__,
        metadata={"kwargs": kwargs, "result": result},
    )
    log_trace_event(
        event_type="reflex_run",
        reflex=__name__,
        source=__name__,
        tags=["reflex", "<your_tag>"],
        metadata={"kwargs": kwargs, "result": result},
    )
    return result

if __name__ == "__main__":
    print(run())

5) Canonical CLI Tool Template (Dispatch‑Safe)

# /tools/<your_tool_name>.py
"""
Tool: <your_tool_name>
Phase: <REQUIRED_PHASE_INT>
Purpose: <one-line purpose>
"""

from boot.boot_path_initializer import inject_paths
inject_paths()

from configs.ironroot_manifest_loader import get_current_phase
from core.memory_log_db import log_memory_event
from core.trace_logger import log_trace_event

REQUIRED_PHASE = <REQUIRED_PHASE_INT>

def run_cli(*args):
    if get_current_phase() < REQUIRED_PHASE:
        raise RuntimeError("❌ Not allowed in this phase")

    result = {"status": "ok", "args": list(args)}

    log_memory_event(
        event_type="cli_command",
        phase=REQUIRED_PHASE,
        source=__name__,
        metadata={"args": list(args), "result": result},
    )
    log_trace_event(
        event_type="cli_command",
        reflex=__name__,
        source=__name__,
        tags=["cli", "<your_tag>"],
        metadata={"args": list(args), "result": result},
    )
    print(result)

if __name__ == "__main__":
    import sys
    run_cli(*sys.argv[1:])

6) Phase Integrity Test — canonical
(Name it /tests/test_phase_<X_Y>_integrity.py and update imports/phase numbers.)

# /tests/test_phase_<X_Y>_integrity.py
from boot.boot_path_initializer import inject_paths
inject_paths()

from configs.ironroot_manifest_loader import get_current_phase
from core.trace_logger import log_trace_event
from core.memory_log_db import log_memory_event

REQUIRED_PHASE = <X.Y as int or floor int>

def run():
    assert get_current_phase() >= REQUIRED_PHASE, "Phase lock error"
    log_memory_event(event_type="test_run", phase=REQUIRED_PHASE, source=__name__, metadata={"suite":"integrity"})
    log_trace_event(event_type="test_run", reflex=__name__, source=__name__, tags=["test","phase"], metadata={"suite":"integrity"})
    print("✅ Phase integrity test passed")

if __name__ == "__main__":
    run()

7) Trace + Memory Drift Sentinel (Phase ≥ 0.4)
(CLI guard to ensure dual‑logging + phase lock are present across files.)

# /tools/reflex_compliance_guard.py
"""
Tool: reflex_compliance_guard
Phase: 0.4
Purpose: Scan reflexes/tools for phase lock + dual logging + manifest sync.
"""
from boot.boot_path_initializer import inject_paths
inject_paths()

from configs.ironroot_manifest_loader import get_current_phase
from core.memory_log_db import log_memory_event
from core.trace_logger import log_trace_event
import os, re, json

REQUIRED_PHASE = 0.4

def _scan_file(path):
    text = open(path, "r", encoding="utf-8", errors="ignore").read()
    checks = {
        "phase_lock": "get_current_phase" in text,
        "memory_log": "log_memory_event" in text,
        "trace_log": "log_trace_event" in text,
    }
    return checks

def run_cli(root="."):
    if get_current_phase() < REQUIRED_PHASE:
        raise RuntimeError("❌ Not allowed in this phase")

    report = []
    for base, _, files in os.walk(root):
        for f in files:
            if f.endswith(".py") and ("reflexes" in base or "tools" in base):
                path = os.path.join(base, f).replace("\\","/")
                checks = _scan_file(path)
                report.append({"file": path, **checks})

    log_memory_event(event_type="compliance_scan", phase=REQUIRED_PHASE, source=__name__, metadata={"count": len(report)})
    log_trace_event(event_type="compliance_scan", reflex=__name__, source=__name__, tags=["compliance","scan"], metadata={"count": len(report)})

    print("🧠 Reflex Compliance Guard — Scan Report")
    bad = 0
    for r in report:
        if not all([r["phase_lock"], r["memory_log"], r["trace_log"]]):
            bad += 1
            print(f"❌ {r['file']}: phase_lock={r['phase_lock']} memory_log={r['memory_log']} trace_log={r['trace_log']}")
    if bad == 0:
        print("✅ All scanned files compliant")

if __name__ == "__main__":
    run_cli(".")

8) Trace Inspector — standard filters
(Already in your tree; template here for consistency.)



# /tools/trace_inspector.py
"""
Tool: trace_inspector
Phase: 0.3
Purpose: Filter /logs/reflex_trace_log.json by tag/source/reflex/time window.
"""
from boot.boot_path_initializer import inject_paths
inject_paths()

from configs.ironroot_manifest_loader import get_current_phase
from core.memory_log_db import log_memory_event
import json, sys

REQUIRED_PHASE = 0.3
TRACE_PATH = "logs/reflex_trace_log.json"

def run_cli(*args):
    if get_current_phase() < REQUIRED_PHASE:
        raise RuntimeError("❌ Not allowed in this phase")

    tag = None
    for i,a in enumerate(args):
        if a == "--tag" and i+1 < len(args): tag = args[i+1]

    try:
        data = json.load(open(TRACE_PATH, "r", encoding="utf-8"))
        rows = [r for r in data if (not tag or tag in (r.get("tags") or []))]
        for r in rows: print(json.dumps(r, ensure_ascii=False))
        log_memory_event(event_type="trace_inspect", phase=REQUIRED_PHASE, source=__name__, metadata={"count": len(rows), "tag": tag})
    except FileNotFoundError:
        print("⚠️ No trace file found:", TRACE_PATH)

if __name__ == "__main__":
    run_cli(*sys.argv[1:])


9) Verify Log Integrity — standard
(Checks UTF‑8, list shape, and basic structure.)
# /tools/verify_log_integrity.py
"""
Tool: verify_log_integrity
Phase: 0.3
Purpose: Ensure log files are UTF‑8 and well‑formed lists.
"""
from boot.boot_path_initializer import inject_paths
inject_paths()

from configs.ironroot_manifest_loader import get_current_phase
from core.memory_log_db import log_memory_event
import json, sys

REQUIRED_PHASE = 0.3
FILES = ["logs/boot_trace_log.json", "logs/reflex_trace_log.json", "logs/will_memory_log.json"]

def run_cli():
    if get_current_phase() < REQUIRED_PHASE:
        raise RuntimeError("❌ Not allowed in this phase")

    ok = True
    for p in FILES:
        try:
            v = json.load(open(p, "r", encoding="utf-8"))
            if not isinstance(v, list): ok = False; print(f"❌ {p}: not a list")
        except Exception as e:
            ok = False; print(f"❌ {p}: {e}")
    log_memory_event(event_type="verify_logs", phase=REQUIRED_PHASE, source=__name__, metadata={"ok": ok})
    print("✅ Logs OK" if ok else "❌ Log integrity issues detected")

if __name__ == "__main__":
    run_cli()

10) Quick Use Checklist (pin this)
Use the Phase Seed template to kick off a phase.

Update manifest + file history with the snippets.

Generate code only from the Canonical Reflex / CLI Tool templates.

Add the Phase Integrity Test and run it.

Run inspectors:

trace_inspector, verify_log_integrity, reflex_compliance_guard (≥0.4)

Append build_log & phase_history with the provided patterns.

If anything violates IronRoot: stop and return the violation message.
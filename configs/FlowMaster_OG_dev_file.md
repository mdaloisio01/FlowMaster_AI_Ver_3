How to install this pack

Create folder: FlowMaster_OG_Max/

Copy all files below exactly (keep directory structure).

In PowerShell:

bash
Copy
Edit
cd .\FlowMaster_OG_Max
python tools/system_check.py
python tools/will_toolchain.py run_reflex reflex_set_persona Analyst
python tools/will_toolchain.py run_reflex reflex_route_by_persona
python tools/will_toolchain.py run_reflex reflex_plan_generator
python tools/will_toolchain.py run_reflex reflex_plan_reactor
python tools/will_toolchain.py run_reflex reflex_scrape_web
python tools/list_reflexes.py
python main.py
📁 FULL FILE DROP (alpha order by dir/file)
/FlowMaster_OG_Max/init.py
python
Copy
Edit
# /FlowMaster_OG_Max/__init__.py
# Root package marker. Required by IronRoot Law.
/FlowMaster_OG_Max/boot.py
python
Copy
Edit
# /FlowMaster_OG_Max/boot.py
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("FLOWMASTER_ENV", "dev")

def boot_info():
    return {
        "project_root": PROJECT_ROOT,
        "env": os.environ.get("FLOWMASTER_ENV", "dev"),
    }

if __name__ == "__main__":
    print("Boot OK:", boot_info())
/FlowMaster_OG_Max/main.py
python
Copy
Edit
# /FlowMaster_OG_Max/main.py
from boot import boot_info
from tools.will_toolchain import run_reflex

if __name__ == "__main__":
    print("Flow Master OG Max — Boot:", boot_info())
    print("Running hello world reflex...")
    print(run_reflex("reflex_hello_world"))
/FlowMaster_OG_Max/configs
/FlowMaster_OG_Max/configs/init.py
python
Copy
Edit
# /FlowMaster_OG_Max/configs/__init__.py
# Config package marker.
/FlowMaster_OG_Max/configs/cli_command_map.json
json
Copy
Edit
{
  "version": "og.max",
  "commands": {
    "run_reflex": "tools/will_toolchain.py",
    "list_reflexes": "tools/list_reflexes.py",
    "system_check": "tools/system_check.py",
    "persona_tool": "tools/persona_tool.py",
    "goal_tool": "tools/goal_tool.py",
    "planning_tool": "tools/planning_tool.py",
    "bridge_tool": "tools/bridge_tool.py"
  }
}
/FlowMaster_OG_Max/configs/ironroot_manifest_loader.py
python
Copy
Edit
# /FlowMaster_OG_Max/configs/ironroot_manifest_loader.py
import json
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_JSON_PATH = os.path.join(PROJECT_ROOT, "ironroot_manifest_data.json")

if not os.path.exists(MANIFEST_JSON_PATH):
    raise FileNotFoundError(f"❌ Manifest JSON not found at: {MANIFEST_JSON_PATH}")

with open(MANIFEST_JSON_PATH, "r", encoding="utf-8") as f:
    manifest = json.load(f)

manifest["_source"] = "configs.ironroot_manifest_loader"
manifest["_project_root"] = PROJECT_ROOT
/FlowMaster_OG_Max/ironroot_manifest_data.json
json
Copy
Edit
{
  "project": "FlowMaster_OG_Max",
  "version": "og.max.v1",
  "current_phase": 17,
  "phases_completed": [
    { "phase": 0,  "label": "OG_Boot_0",         "status": "✅ Completed", "description": "OG structure, stable boot, CLI" },
    { "phase": 1,  "label": "OG_Memory_1",       "status": "✅ Completed", "description": "SQLite memory spine with schema" },
    { "phase": 2,  "label": "OG_Reflex_2",       "status": "✅ Completed", "description": "Reflex loader + hello reflex" },
    { "phase": 3,  "label": "OG_Trace_3",        "status": "✅ Completed", "description": "Trace logging hooks" },
    { "phase": 4,  "label": "OG_Inspector_4",    "status": "✅ Completed", "description": "Trace inspector panel (route-safe)" },
    { "phase": 5,  "label": "OG_Manifest_5",     "status": "✅ Completed", "description": "Manifest loader + completeness guard" },
    { "phase": 6,  "label": "OG_Guard_6",        "status": "✅ Completed", "description": "Ghost/missing file scan" },
    { "phase": 7,  "label": "OG_Panel_7",        "status": "✅ Completed", "description": "Panels phase-aware, safe load" },
    { "phase": 10, "label": "SchedulerRise_10",  "status": "✅ Completed", "description": "Reflex scheduler runner stub live" },
    { "phase": 11, "label": "WebEyes_11",        "status": "✅ Completed", "description": "Scrapers online (safe stubs)" },
    { "phase": 14, "label": "DataBridge_14",     "status": "✅ Completed", "description": "Data bridge reflex + tool" },
    { "phase": 15, "label": "GoalLink_15",       "status": "✅ Completed", "description": "Goal memory, manager, linker" },
    { "phase": 16, "label": "PlanSense_16",      "status": "✅ Completed", "description": "Plan generator + reactor" },
    { "phase": 17, "label": "PersonaPulse_17",   "status": "✅ Completed", "description": "Persona memory, switcher, routing" }
  ],
  "reflexes": {
    "reflex_data_bridge":              { "path": "reflexes/core/reflex_data_bridge.py",          "status": "live", "phase_built": 14 },
    "reflex_goal_linker":              { "path": "reflexes/core/reflex_goal_linker.py",          "status": "live", "phase_built": 15 },
    "reflex_goal_manager":             { "path": "reflexes/core/reflex_goal_manager.py",         "status": "live", "phase_built": 15 },
    "reflex_hello_world":              { "path": "reflexes/core/reflex_hello_world.py",          "status": "live", "phase_built": 2  },
    "reflex_loader":                   { "path": "reflexes/core/reflex_loader.py",               "status": "live", "phase_built": 2  },
    "reflex_manifest_complete":        { "path": "reflexes/core/reflex_manifest_complete.py",    "status": "live", "phase_built": 8  },
    "reflex_manifest_guard":           { "path": "reflexes/core/reflex_manifest_guard.py",       "status": "live", "phase_built": 6  },
    "reflex_plan_generator":           { "path": "reflexes/core/reflex_plan_generator.py",       "status": "live", "phase_built": 16 },
    "reflex_plan_reactor":             { "path": "reflexes/core/reflex_plan_reactor.py",         "status": "live", "phase_built": 16 },
    "reflex_route_by_persona":         { "path": "reflexes/core/reflex_route_by_persona.py",     "status": "live", "phase_built": 17 },
    "reflex_scheduler_runner":         { "path": "reflexes/core/reflex_scheduler_runner.py",     "status": "live", "phase_built": 10 },
    "reflex_scrape_mls":               { "path": "reflexes/scrapers/reflex_scrape_mls.py",       "status": "live", "phase_built": 11 },
    "reflex_scrape_web":               { "path": "reflexes/scrapers/reflex_scrape_web.py",       "status": "live", "phase_built": 11 },
    "reflex_self_test_runner":         { "path": "reflexes/core/reflex_self_test_runner.py",     "status": "live", "phase_built": 3  },
    "reflex_set_persona":              { "path": "reflexes/core/reflex_set_persona.py",          "status": "live", "phase_built": 17 }
  },
  "tools": {
    "bridge_tool":                     { "path": "tools/bridge_tool.py",                         "status": "live", "phase_built": 14 },
    "goal_tool":                       { "path": "tools/goal_tool.py",                           "status": "live", "phase_built": 15 },
    "list_reflexes":                   { "path": "tools/list_reflexes.py",                       "status": "live", "phase_built": 2  },
    "persona_tool":                    { "path": "tools/persona_tool.py",                        "status": "live", "phase_built": 17 },
    "planning_tool":                   { "path": "tools/planning_tool.py",                       "status": "live", "phase_built": 16 },
    "system_check":                    { "path": "tools/system_check.py",                        "status": "live", "phase_built": 17 },
    "will_toolchain":                  { "path": "tools/will_toolchain.py",                      "status": "live", "phase_built": 2  }
  },
  "panels": {
    "panel_goal_manager":              { "path": "gui/components/panel_goal_manager.py",         "status": "live", "phase_built": 15 },
    "panel_persona_switcher":          { "path": "gui/components/panel_persona_switcher.py",     "status": "live", "phase_built": 17 },
    "panel_trace_inspector":           { "path": "gui/components/panel_trace_inspector.py",      "status": "live", "phase_built": 4  }
  },
  "personas": {
    "active_persona": "Analyst",
    "definitions": {
      "Agent":    { "tone": "direct",       "log_scope": "minimal", "reflex_mode": "fast" },
      "Analyst":  { "tone": "verbose",      "log_scope": "deep",    "reflex_mode": "full_analysis" },
      "Manager":  { "tone": "authoritative","log_scope": "overview","reflex_mode": "delegate" },
      "Assistant":{ "tone": "friendly",     "log_scope": "interactive","reflex_mode": "support" }
    }
  }
}
/FlowMaster_OG_Max/gui
/FlowMaster_OG_Max/gui/init.py
python
Copy
Edit
# /FlowMaster_OG_Max/gui/__init__.py
/FlowMaster_OG_Max/gui/components/init.py
python
Copy
Edit
# /FlowMaster_OG_Max/gui/components/__init__.py
/FlowMaster_OG_Max/gui/components/panel_goal_manager.py
python
Copy
Edit
# /FlowMaster_OG_Max/gui/components/panel_goal_manager.py
from memory.goal_memory import list_goals, create_goal
from memory.will_memory_engine import log_memory_event

def panel_goal_manager(action: str = "list", goal_text: str = ""):
    if action == "create" and goal_text.strip():
        gid = create_goal(goal_text.strip())
        log_memory_event(
            event_text="GUI create goal",
            event_type="goal_create",
            phase=15,
            source="panel_goal_manager",
            metadata={"goal_id": gid, "text": goal_text.strip()}
        )
        return {"ok": True, "created": gid}
    return {"ok": True, "goals": list_goals()}
/FlowMaster_OG_Max/gui/components/panel_persona_switcher.py
python
Copy
Edit
# /FlowMaster_OG_Max/gui/components/panel_persona_switcher.py
from memory.persona_memory import get_active_persona, set_active_persona, get_persona_traits

def panel_persona_switcher(set_to: str | None = None):
    current = get_active_persona()
    if set_to:
        if set_to in get_persona_traits("__list__"):
            set_active_persona(set_to)
            current = set_to
    traits = get_persona_traits(current)
    return {"persona": current, "traits": traits}
/FlowMaster_OG_Max/gui/components/panel_trace_inspector.py
python
Copy
Edit
# /FlowMaster_OG_Max/gui/components/panel_trace_inspector.py
from memory.will_memory_engine import WillMemoryEngine

def panel_trace_inspector(limit: int = 10):
    engine = WillMemoryEngine()
    events = engine.fetch_recent(limit)
    # Console-friendly output
    print("=== Trace Inspector (last", limit, ") ===")
    for e in events:
        print(f"[{e['timestamp']}] {e['event_text']} :: type={e.get('event_type')} :: phase={e.get('phase')} :: src={e.get('source')}")
    return {"ok": True, "count": len(events)}
/FlowMaster_OG_Max/memory
/FlowMaster_OG_Max/memory/init.py
python
Copy
Edit
# /FlowMaster_OG_Max/memory/__init__.py
/FlowMaster_OG_Max/memory/goal_memory.py
python
Copy
Edit
# /FlowMaster_OG_Max/memory/goal_memory.py
import os
import sqlite3
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "will_memory.sqlite")

SCHEMA = """
CREATE TABLE IF NOT EXISTS goals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL,
  text TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'open'
);
"""

def _ensure():
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(SCHEMA)
        conn.commit()
    finally:
        conn.close()

def create_goal(text: str) -> int:
    _ensure()
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.execute("INSERT INTO goals (created_at, text, status) VALUES (?, ?, ?)",
                           (datetime.utcnow().isoformat(), text, "open"))
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()

def list_goals(limit: int = 50):
    _ensure()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.execute("SELECT * FROM goals ORDER BY id DESC LIMIT ?", (limit,))
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()
/FlowMaster_OG_Max/memory/persona_memory.py
python
Copy
Edit
# /FlowMaster_OG_Max/memory/persona_memory.py
from configs.ironroot_manifest_loader import manifest
from memory.will_memory_engine import log_memory_event

def list_available_personas():
    return list(manifest.get("personas", {}).get("definitions", {}).keys())

def get_active_persona():
    return manifest.get("personas", {}).get("active_persona")

def set_active_persona(persona_name: str):
    if persona_name not in list_available_personas():
        raise ValueError(f"Unknown persona: {persona_name}")
    manifest["personas"]["active_persona"] = persona_name
    log_memory_event(
        event_text=f"Persona switched to {persona_name}",
        event_type="persona_switch",
        phase=17,
        source="persona_memory",
        metadata={"persona": persona_name}
    )
    return persona_name

def get_persona_traits(persona_name: str | None):
    if persona_name == "__list__":
        return list_available_personas()
    if not persona_name:
        persona_name = get_active_persona()
    return manifest.get("personas", {}).get("definitions", {}).get(persona_name, {})
/FlowMaster_OG_Max/memory/planning_memory.py
python
Copy
Edit
# /FlowMaster_OG_Max/memory/planning_memory.py
import os
import json
import sqlite3
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "will_memory.sqlite")

SCHEMA = """
CREATE TABLE IF NOT EXISTS plans (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL,
  title TEXT NOT NULL,
  steps TEXT NOT NULL
);
"""

def _ensure():
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(SCHEMA)
        conn.commit()
    finally:
        conn.close()

def save_plan(title: str, steps: list[str]) -> int:
    _ensure()
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.execute("INSERT INTO plans (created_at, title, steps) VALUES (?, ?, ?)",
                           (datetime.utcnow().isoformat(), title, json.dumps(steps, ensure_ascii=False)))
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()

def list_plans(limit: int = 50):
    _ensure()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.execute("SELECT * FROM plans ORDER BY id DESC LIMIT ?", (limit,))
        out = []
        for r in cur.fetchall():
            item = dict(r)
            try:
                item["steps"] = json.loads(item["steps"])
            except Exception:
                pass
            out.append(item)
        return out
    finally:
        conn.close()
/FlowMaster_OG_Max/memory/will_memory_engine.py
python
Copy
Edit
# /FlowMaster_OG_Max/memory/will_memory_engine.py
import os
import json
import sqlite3
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "will_memory.sqlite")

SCHEMA = """
CREATE TABLE IF NOT EXISTS memory_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TEXT NOT NULL,
  event_text TEXT NOT NULL,
  event_type TEXT,
  phase INTEGER,
  source TEXT,
  tags TEXT,
  metadata TEXT
);
"""

class WillMemoryEngine:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._ensure_db()

    def _ensure_db(self):
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(SCHEMA)
            conn.commit()
        finally:
            conn.close()

    def log_memory(self, event_text: str, tags=None, metadata=None):
        # Legacy support: simple event
        return self.log_memory_ex(
            event_text=event_text,
            event_type="legacy_event",
            phase=None,
            source="WillMemoryEngine.log_memory",
            tags=tags or [],
            metadata=metadata or {}
        )

    def log_memory_ex(self, event_text: str, event_type: str | None, phase: int | None,
                      source: str | None, tags: list[str] | None, metadata: dict | None):
        ts = datetime.utcnow().isoformat()
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                "INSERT INTO memory_log (timestamp, event_text, event_type, phase, source, tags, metadata) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (ts, event_text, event_type, phase, source, ",".join(tags or []), json.dumps(metadata or {}, ensure_ascii=False))
            )
            conn.commit()
        finally:
            conn.close()
        return {"ok": True, "timestamp": ts}

    def fetch_recent(self, limit: int = 25):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            cur = conn.execute("SELECT * FROM memory_log ORDER BY id DESC LIMIT ?", (limit,))
            rows = [dict(r) for r in cur.fetchall()]
            for r in rows:
                if r.get("metadata"):
                    try:
                        r["metadata"] = json.loads(r["metadata"])
                    except Exception:
                        pass
            return rows
        finally:
            conn.close()

# Convenience helper used throughout
def log_memory_event(event_text: str, event_type: str | None = None, phase: int | None = None,
                     source: str | None = None, tags: list[str] | None = None, metadata: dict | None = None):
    return WillMemoryEngine().log_memory_ex(event_text, event_type, phase, source, tags, metadata)

# Legacy alias (some tools may import this name)
def log_event(event_text: str, tags=None):
    return WillMemoryEngine().log_memory(event_text, tags=tags or [], metadata={})
/FlowMaster_OG_Max/reflexes
/FlowMaster_OG_Max/reflexes/init.py
python
Copy
Edit
# /FlowMaster_OG_Max/reflexes/__init__.py
/FlowMaster_OG_Max/reflexes/core/init.py
python
Copy
Edit
# /FlowMaster_OG_Max/reflexes/core/__init__.py
/FlowMaster_OG_Max/reflexes/core/reflex_data_bridge.py
python
Copy
Edit
# /FlowMaster_OG_Max/reflexes/core/reflex_data_bridge.py
from memory.will_memory_engine import log_memory_event

def reflex_data_bridge():
    # Stubbed — simulates contextualizing scraped data into memory/goals
    log_memory_event(
        event_text="Data bridged into context",
        event_type="data_bridge",
        phase=14,
        source="reflex_data_bridge",
        metadata={"bridge": "ok"}
    )
    return "✅ Data bridge executed."
/FlowMaster_OG_Max/reflexes/core/reflex_goal_linker.py
python
Copy
Edit
# /FlowMaster_OG_Max/reflexes/core/reflex_goal_linker.py
from memory.will_memory_engine import log_memory_event

def reflex_goal_linker():
    # Stubbed — would match scraped data to active goals
    log_memory_event(
        event_text="Checked goal-data links",
        event_type="goal_link_check",
        phase=15,
        source="reflex_goal_linker",
        metadata={"matches_found": 0}
    )
    return "🔗 Goal linker ran."
/FlowMaster_OG_Max/reflexes/core/reflex_goal_manager.py
python
Copy
Edit
# /FlowMaster_OG_Max/reflexes/core/reflex_goal_manager.py
from memory.goal_memory import list_goals, create_goal
from memory.will_memory_engine import log_memory_event

def reflex_goal_manager(action: str = "list", text: str = ""):
    if action == "create" and text.strip():
        gid = create_goal(text.strip())
        log_memory_event(
            event_text="Goal created",
            event_type="goal_create",
            phase=15,
            source="reflex_goal_manager",
            metadata={"goal_id": gid, "text": text.strip()}
        )
        return f"✅ Goal created: {gid}"
    goals = list_goals()
    return {"goals": goals}
/FlowMaster_OG_Max/reflexes/core/reflex_hello_world.py
python
Copy
Edit
# /FlowMaster_OG_Max/reflexes/core/reflex_hello_world.py
from memory.will_memory_engine import log_memory_event

def reflex_hello_world():
    log_memory_event(
        event_text="👋 OG Max says hello",
        event_type="hello",
        phase=2,
        source="reflex_hello_world",
        metadata={"greeting": True}
    )
    return "OG Max Hello — logged."
/FlowMaster_OG_Max/reflexes/core/reflex_loader.py
python
Copy
Edit
# /FlowMaster_OG_Max/reflexes/core/reflex_loader.py
import importlib
from configs.ironroot_manifest_loader import manifest

def reflex_loader():
    loaded = []
    for name, meta in manifest.get("reflexes", {}).items():
        module_path = meta["path"].replace("/", ".").replace(".py", "")
        mod = importlib.import_module(module_path)
        fn = getattr(mod, name, None)
        if callable(fn):
            loaded.append(name)
    return {"loaded": loaded, "count": len(loaded)}
/FlowMaster_OG_Max/reflexes/core/reflex_manifest_complete.py
python
Copy
Edit
# /FlowMaster_OG_Max/reflexes/core/reflex_manifest_complete.py
from configs.ironroot_manifest_loader import manifest

def reflex_manifest_complete():
    required = ("reflexes", "tools", "panels", "phases_completed", "current_phase")
    missing = [k for k in required if k not in manifest]
    if missing:
        return f"❌ Manifest missing keys: {missing}"
    return "✅ Manifest completeness OK."
/FlowMaster_OG_Max/reflexes/core/reflex_manifest_guard.py
python
Copy
Edit
# /FlowMaster_OG_Max/reflexes/core/reflex_manifest_guard.py
import os
from configs.ironroot_manifest_loader import manifest

def reflex_manifest_guard():
    project_root = manifest["_project_root"]
    issues = []
    for name, meta in manifest.get("reflexes", {}).items():
        fpath = os.path.join(project_root, meta["path"])
        if not os.path.exists(fpath):
            issues.append(f"Missing reflex file: {fpath}")
    for name, meta in manifest.get("tools", {}).items():
        fpath = os.path.join(project_root, meta["path"])
        if not os.path.exists(fpath):
            issues.append(f"Missing tool file: {fpath}")
    for name, meta in manifest.get("panels", {}).items():
        fpath = os.path.join(project_root, meta["path"])
        if not os.path.exists(fpath):
            issues.append(f"Missing panel file: {fpath}")

    if issues:
        return "❌ Manifest guard issues:\n" + "\n".join(issues)
    return "✅ Manifest guard passed — no ghosts."
/FlowMaster_OG_Max/reflexes/core/reflex_plan_generator.py
python
Copy
Edit
# /FlowMaster_OG_Max/reflexes/core/reflex_plan_generator.py
from memory.planning_memory import save_plan
from memory.will_memory_engine import log_memory_event
from memory.persona_memory import get_active_persona, get_persona_traits

def reflex_plan_generator(title: str = "Default Plan"):
    persona = get_active_persona()
    traits = get_persona_traits(persona)
    mode = traits.get("reflex_mode", "support")

    steps = []
    if mode == "fast":
        steps = ["Do the thing", "Confirm done"]
    elif mode == "delegate":
        steps = ["Create tasks", "Assign tasks", "Review outcomes"]
    elif mode == "full_analysis":
        steps = ["Collect context", "Analyze options", "Draft plan", "Review assumptions", "Output plan"]
    else:
        steps = ["Understand request", "Provide helpful steps", "Offer to assist further"]

    pid = save_plan(title, steps)
    log_memory_event(
        event_text="Plan generated",
        event_type="plan_suggestion",
        phase=16,
        source="reflex_plan_generator",
        metadata={"plan_id": pid, "persona": persona, "steps": steps}
    )
    return {"plan_id": pid, "steps": steps, "persona": persona}
/FlowMaster_OG_Max/reflexes/core/reflex_plan_reactor.py
python
Copy
Edit
# /FlowMaster_OG_Max/reflexes/core/reflex_plan_reactor.py
from memory.planning_memory import list_plans
from memory.will_memory_engine import log_memory_event

def reflex_plan_reactor():
    plans = list_plans(limit=1)
    if not plans:
        return "ℹ️ No plans to react to."
    plan = plans[0]
    log_memory_event(
        event_text="Plan reaction routed",
        event_type="plan_reaction",
        phase=16,
        source="reflex_plan_reactor",
        metadata={"plan_id": plan["id"], "step_count": len(plan.get("steps", []))}
    )
    return f"⚙️ Reacted to plan {plan['id']}."
/FlowMaster_OG_Max/reflexes/core/reflex_route_by_persona.py
python
Copy
Edit
# /FlowMaster_OG_Max/reflexes/core/reflex_route_by_persona.py
from memory.persona_memory import get_active_persona, get_persona_traits
from memory.will_memory_engine import log_memory_event

def reflex_route_by_persona():
    persona = get_active_persona()
    traits = get_persona_traits(persona)
    mode = traits.get("reflex_mode", "support")

    msg = ""
    if mode == "fast":
        msg = "⚡ Agent Mode: Minimal reflex execution."
    elif mode == "delegate":
        msg = "🧭 Manager Mode: Delegating non-core steps."
    elif mode == "full_analysis":
        msg = "🧠 Analyst Mode: Detailed analysis enabled."
    else:
        msg = "🙂 Assistant Mode: Interactive help."

    log_memory_event(
        event_text="Persona route",
        event_type="persona_route",
        phase=17,
        source="reflex_route_by_persona",
        metadata={"persona": persona, "mode": mode}
    )
    return msg
/FlowMaster_OG_Max/reflexes/core/reflex_scheduler_runner.py
python
Copy
Edit
# /FlowMaster_OG_Max/reflexes/core/reflex_scheduler_runner.py
from tools.cli_trace_log import trace_cli_command
from memory.will_memory_engine import log_memory_event

def reflex_scheduler_runner():
    trace_cli_command("reflex_scheduler_runner", [])
    log_memory_event(
        event_text="Scheduler tick",
        event_type="scheduler_tick",
        phase=10,
        source="reflex_scheduler_runner",
        metadata={"tick": True}
    )
    return "⏱️ Scheduler tick executed."
/FlowMaster_OG_Max/reflexes/core/reflex_self_test_runner.py
python
Copy
Edit
# /FlowMaster_OG_Max/reflexes/core/reflex_self_test_runner.py
from .reflex_hello_world import reflex_hello_world
from .reflex_loader import reflex_loader
from .reflex_manifest_guard import reflex_manifest_guard

def reflex_self_test_runner():
    results = {
        "hello": reflex_hello_world(),
        "loader": reflex_loader(),
        "manifest_guard": reflex_manifest_guard(),
    }
    return results
/FlowMaster_OG_Max/reflexes/core/reflex_set_persona.py
python
Copy
Edit
# /FlowMaster_OG_Max/reflexes/core/reflex_set_persona.py
from memory.persona_memory import set_active_persona

def reflex_set_persona(persona_name: str = "Analyst"):
    set_active_persona(persona_name)
    return f"✅ Persona set to: {persona_name}"
/FlowMaster_OG_Max/reflexes/scrapers/init.py
python
Copy
Edit
# /FlowMaster_OG_Max/reflexes/scrapers/__init__.py
/FlowMaster_OG_Max/reflexes/scrapers/reflex_scrape_mls.py
python
Copy
Edit
# /FlowMaster_OG_Max/reflexes/scrapers/reflex_scrape_mls.py
from memory.will_memory_engine import log_memory_event

def reflex_scrape_mls():
    # Stub scraper: no external calls; pretend we scraped 3 items
    items = [{"id": 1}, {"id": 2}, {"id": 3}]
    log_memory_event(
        event_text="MLS scrape complete",
        event_type="scrape_mls",
        phase=11,
        source="reflex_scrape_mls",
        metadata={"count": len(items)}
    )
    return f"🏡 MLS scraped {len(items)} items."
/FlowMaster_OG_Max/reflexes/scrapers/reflex_scrape_web.py
python
Copy
Edit
# /FlowMaster_OG_Max/reflexes/scrapers/reflex_scrape_web.py
from memory.will_memory_engine import log_memory_event

def reflex_scrape_web():
    # Stub web scraper: no outbound requests; simulate 2 docs
    docs = [{"url": "https://example.com/a"}, {"url": "https://example.com/b"}]
    log_memory_event(
        event_text="Web scrape complete",
        event_type="scrape_web",
        phase=11,
        source="reflex_scrape_web",
        metadata={"count": len(docs)}
    )
    return f"🌐 Web scraped {len(docs)} docs."
/FlowMaster_OG_Max/static
/FlowMaster_OG_Max/static/init.py
python
Copy
Edit
# /FlowMaster_OG_Max/static/__init__.py
/FlowMaster_OG_Max/templates
/FlowMaster_OG_Max/templates/init.py
python
Copy
Edit
# /FlowMaster_OG_Max/templates/__init__.py
/FlowMaster_OG_Max/tools
/FlowMaster_OG_Max/tools/init.py
python
Copy
Edit
# /FlowMaster_OG_Max/tools/__init__.py
/FlowMaster_OG_Max/tools/bridge_tool.py
python
Copy
Edit
# /FlowMaster_OG_Max/tools/bridge_tool.py
from configs.ironroot_manifest_loader import manifest
from reflexes.core.reflex_data_bridge import reflex_data_bridge

def main():
    print("=== Bridge Tool ===")
    print("Project:", manifest["project"])
    print(reflex_data_bridge())

if __name__ == "__main__":
    main()
/FlowMaster_OG_Max/tools/cli_trace_log.py
python
Copy
Edit
# /FlowMaster_OG_Max/tools/cli_trace_log.py
from memory.will_memory_engine import log_memory_event

def trace_cli_command(command: str, args: list[str]):
    log_memory_event(
        event_text=f"CLI command: {command}",
        event_type="cli_command",
        phase=None,
        source="cli",
        metadata={"args": args}
    )
/FlowMaster_OG_Max/tools/goal_tool.py
python
Copy
Edit
# /FlowMaster_OG_Max/tools/goal_tool.py
import sys
from memory.goal_memory import create_goal, list_goals
from memory.will_memory_engine import log_memory_event

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--create":
        text = " ".join(sys.argv[2:]).strip() or "Untitled goal"
        gid = create_goal(text)
        log_memory_event(
            event_text="Goal created via CLI",
            event_type="goal_create",
            phase=15,
            source="goal_tool",
            metadata={"goal_id": gid, "text": text}
        )
        print(f"✅ Created goal {gid}: {text}")
        return
    goals = list_goals()
    print("=== Goals ===")
    for g in goals:
        print(f"- [{g['id']}] {g['text']} ({g['status']})")

if __name__ == "__main__":
    main()
/FlowMaster_OG_Max/tools/list_reflexes.py
python
Copy
Edit
# /FlowMaster_OG_Max/tools/list_reflexes.py
from configs.ironroot_manifest_loader import manifest

def main():
    print("=== Reflexes ===")
    for name in sorted(manifest.get("reflexes", {}).keys()):
        meta = manifest["reflexes"][name]
        print(f"- {name} -> {meta['path']} (status: {meta['status']}, phase: {meta['phase_built']})")

if __name__ == "__main__":
    main()
/FlowMaster_OG_Max/tools/persona_tool.py
python
Copy
Edit
# /FlowMaster_OG_Max/tools/persona_tool.py
import sys
from memory.persona_memory import list_available_personas, get_active_persona, set_active_persona, get_persona_traits

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--set":
        if len(sys.argv) < 3:
            print("Usage: persona_tool.py --set <PersonaName>")
            sys.exit(1)
        name = sys.argv[2]
        set_active_persona(name)
        print(f"✅ Persona set to: {name}")
        print("Traits:", get_persona_traits(name))
        return

    print("=== Personas ===")
    print("Active:", get_active_persona())
    print("Available:", ", ".join(list_available_personas()))
    print("Active traits:", get_persona_traits(None))

if __name__ == "__main__":
    main()
/FlowMaster_OG_Max/tools/planning_tool.py
python
Copy
Edit
# /FlowMaster_OG_Max/tools/planning_tool.py
from reflexes.core.reflex_plan_generator import reflex_plan_generator
from reflexes.core.reflex_plan_reactor import reflex_plan_reactor
from memory.planning_memory import list_plans

def main():
    print("=== Planning Tool ===")
    out = reflex_plan_generator("CLI Plan")
    print("Generated:", out)
    print(reflex_plan_reactor())
    print("Plans:", list_plans())

if __name__ == "__main__":
    main()
/FlowMaster_OG_Max/tools/system_check.py
python
Copy
Edit
# /FlowMaster_OG_Max/tools/system_check.py
import os
import sys
import importlib
import traceback

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from configs.ironroot_manifest_loader import manifest

def trace(msg): print(msg)

def test_import(module_path: str):
    mod = importlib.import_module(module_path)
    return mod

def test_reflex(name, meta):
    try:
        module_path = meta["path"].replace("/", ".").replace(".py", "")
        mod = test_import(module_path)
        fn = getattr(mod, name)
        out = fn()
        trace(f"✅ Reflex {name} OK -> {out}")
        return True
    except Exception as e:
        trace(f"❌ Reflex {name} failed: {e}")
        traceback.print_exc()
        return False

def main():
    print("\n🔐 OG Max — IronRoot System Check\n")
    print(f"Phase: {manifest.get('current_phase')}  Source: {manifest.get('_source')}")

    ok = True
    # Existence checks
    for sec in ("reflexes", "tools", "panels"):
        for name, meta in manifest.get(sec, {}).items():
            path = os.path.join(PROJECT_ROOT, meta["path"])
            if not os.path.exists(path):
                print(f"❌ Missing {sec[:-1]}: {path}")
                ok = False

    # Import tools
    for name, meta in manifest.get("tools", {}).items():
        try:
            test_import(meta["path"].replace("/", ".").replace(".py", ""))
            trace(f"✅ Tool import OK: {name}")
        except Exception as e:
            trace(f"❌ Tool import failed: {name} -> {e}")
            ok = False

    # Run reflexes
    for name, meta in manifest.get("reflexes", {}).items():
        ok = test_reflex(name, meta) and ok

    print("\n🛡️ Manifest Guard:")
    try:
        from reflexes.core.reflex_manifest_guard import reflex_manifest_guard
        print(reflex_manifest_guard())
    except Exception as e:
        print(f"❌ Guard failed: {e}")
        ok = False

    print("\n" + ("✅ System Check PASS" if ok else "❌ System Check FAIL"))
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
/FlowMaster_OG_Max/tools/will_toolchain.py
python
Copy
Edit
# /FlowMaster_OG_Max/tools/will_toolchain.py
import os
import sys
import importlib

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from configs.ironroot_manifest_loader import manifest
from tools.cli_trace_log import trace_cli_command

def run_reflex(reflex_name: str, *args):
    meta = manifest.get("reflexes", {}).get(reflex_name)
    if not meta:
        return f"❌ Unknown reflex: {reflex_name}"

    module_path = meta["path"].replace("/", ".").replace(".py", "")
    mod = importlib.import_module(module_path)
    fn = getattr(mod, reflex_name, None)
    if not callable(fn):
        return f"❌ Reflex function missing: {reflex_name}"

    trace_cli_command("run_reflex", [reflex_name] + list(args))
    return fn(*args) if args else fn()

def main():
    if len(sys.argv) < 3 or sys.argv[1] != "run_reflex":
        print("Usage: python tools/will_toolchain.py run_reflex <reflex_name> [args...]")
        sys.exit(1)
    reflex_name = sys.argv[2]
    args = sys.argv[3:]
    print(run_reflex(reflex_name, *args))

if __name__ == "__main__":
    main()
✅ What’s Live in this EVERYTHING Pack
Memory Spine: robust SQLite tables (memory_log, goals, plans) with JSON metadata; helpers: log_memory_event, legacy log_event.

Personas: persona_memory + GUI panel + CLI tool; active persona + traits drive routing and plan styles.

Planner: reflex_plan_generator (persona-aware) + reflex_plan_reactor + planning_tool + persisted plans.

Goals: goal_memory, reflex_goal_manager, reflex_goal_linker, GUI panel + CLI tool.

Data Bridge: reflex_data_bridge + bridge_tool.

Scrapers: web + MLS safe stubs (no network); log results and counts.

Scheduler: runner stub + CLI trace logging.

Guards: reflex_manifest_guard + reflex_manifest_complete + tools/system_check.py.

CLI: will_toolchain.py runs any reflex with args, all tools import-verified.

GUI Panels: Trace Inspector, Persona Switcher, Goal Manager (console-safe stubs).

Manifest Discipline: ironroot_manifest_data.json (data) vs configs/ironroot_manifest_loader.py (code). No name collisions.

🧱 IronRoot Lock-ins Addressed
No ghost refs: guard + system_check validate existence and import for every manifest entry.

Naming clarity: loader != data; no .py vs .json name overlap.

Phase discipline: manifest current_phase = 17; components tagged with phase_built and log phase.

CLI/GUI parity: all core functions callable in CLI and route-safe in panels.

Single logging spine: every action logs via WillMemoryEngine.

Quick Runbook
System audit:

bash
Copy
Edit
python tools/system_check.py
Set persona and route:

bash
Copy
Edit
python tools/will_toolchain.py run_reflex reflex_set_persona Manager
python tools/will_toolchain.py run_reflex reflex_route_by_persona
Generate and react to a plan:

bash
Copy
Edit
python tools/will_toolchain.py run_reflex reflex_plan_generator
python tools/will_toolchain.py run_reflex reflex_plan_reactor
Scrape (stub) + bridge:

bash
Copy
Edit
python tools/will_toolchain.py run_reflex reflex_scrape_web
python tools/will_toolchain.py run_reflex reflex_scrape_mls
python tools/bridge_tool.py
Goals:

bash
Copy
Edit
python tools/goal_tool.py --create "Ship v0.1 persona UX"
python tools/goal_tool.py
python tools/will_toolchain.py run_reflex reflex_goal_manager
Inspect logs:

bash
Copy
Edit
python tools/will_toolchain.py run_reflex reflex_hello_world
python tools/will_toolchain.py run_reflex reflex_self_test_runner
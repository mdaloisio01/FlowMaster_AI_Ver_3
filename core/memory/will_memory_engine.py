# === IronRoot Phase Guard (auto-injected) ===
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from boot.boot_path_initializer import inject_paths
inject_paths()
from core.phase_control import ensure_phase
REQUIRED_PHASE = 0.7
ensure_phase(REQUIRED_PHASE)
# === /IronRoot Phase Guard ===

# /core/memory/will_memory_engine.py

import os
import json
import datetime

MEMORY_LOG_PATH = "will_memory_log.json"

def load_memory_log():
    if not os.path.exists(MEMORY_LOG_PATH):
        return []
    try:
        with open(MEMORY_LOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_memory_log(log_entries):
    with open(MEMORY_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log_entries, f, indent=2, ensure_ascii=False)

def add_memory_event(event_text, event_type="info", source=None, phase=0, metadata=None):
    log = load_memory_log()
    timestamp = datetime.datetime.now().isoformat()

    new_entry = {
        "timestamp": timestamp,
        "event_text": event_text,
        "event_type": event_type,
        "source": source,
        "phase": phase,
        "metadata": metadata or {}
    }

    log.append(new_entry)
    save_memory_log(log)

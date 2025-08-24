# core/memory_log_db.py
# Purpose: simple helpers around the memory log JSON (+ test-name shims)
# Policy: forward-slash paths, UTF-8 JSON writes, append-not-overwrite

import json
from datetime import datetime
from typing import Any, Dict, List

MEMORY_LOG_PATH = "logs/will_memory_log.json"

def _read_list(path: str) -> List[Dict[str, Any]]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except FileNotFoundError:
        return []
    except Exception:
        return []

def _write_list(path: str, data: List[Dict[str, Any]]) -> None:
    import os
    os.makedirs("/".join(path.split("/")[:-1]) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def insert_memory_log(event_type: str, source: str, tags: List[str], content: Any, phase: float = None, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    if isinstance(tags, str):
        tags = [tags]
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "source": source,
        "tags": tags or [],
        "content": content,
        "phase": phase,
    }
    if metadata:
        entry["metadata"] = metadata
    data = _read_list(MEMORY_LOG_PATH)
    data.append(entry)
    _write_list(MEMORY_LOG_PATH, data)
    return entry

def fetch_memory_logs() -> List[Dict[str, Any]]:
    return _read_list(MEMORY_LOG_PATH)

# --- Test compatibility shims (names some tests expect) ---
def insert_memory_log_entry(event_type, source, tags, content):
    return insert_memory_log(event_type, source, tags, content)

def fetch_all_memory_logs():
    return fetch_memory_logs()

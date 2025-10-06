from boot.boot_path_initializer import inject_paths; inject_paths()
from core.phase_control import ensure_phase
from core.trace_logger import log_trace_event
from core.memory_interface import log_memory_event

REQUIRED_PHASE = 0.4  # minimum allowed
ensure_phase(REQUIRED_PHASE)
log_trace_event("module_import", module=__name__, required_phase=REQUIRED_PHASE)

"""
reflex_registry_scanner.py

Purpose:
  Scan /reflexes for active reflex files not yet declared in the registry.

Phase:
  Phase-locked at 0.4+ (safe to run in later phases).

Behavior:
  - Detects "active" reflex files by simple content heuristics
  - Loads registry from configs/reflex_registry.json (list[str] or dict[str,str])
  - Prints any missing registrations
  - Dual-logs (trace + memory)
"""

from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = PROJECT_ROOT / "configs" / "reflex_registry.json"
REFLEX_DIR = PROJECT_ROOT / "reflexes"

HEURISTIC_TOKENS = (
    "log_memory_event",
    "get_current_phase",
    "def run_cli(",
)

def is_reflex_file(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        log_trace_event(
            "read_error",
            file=str(path),
            error=str(e),
            required_phase=REQUIRED_PHASE,
        )
        return False
    return all(tok in text for tok in HEURISTIC_TOKENS)

def load_registry() -> set:
    if not REGISTRY_PATH.exists():
        print("⚠️  reflex_registry.json not found.")
        return set()
    try:
        data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"❌ Failed to read registry: {e}")
        return set()

    # Accept either list[str] or dict[str, str]
    if isinstance(data, list):
        return {normalize_path(p) for p in data}
    if isinstance(data, dict):
        # values or keys may be paths depending on house style — normalize both
        keys = {normalize_path(k) for k in data.keys()}
        vals = {normalize_path(v) for v in data.values() if isinstance(v, str)}
        return keys | vals
    print("❌ Unsupported registry format (expected list or dict).")
    return set()

def normalize_path(p: str) -> str:
    # Store as posix-style relative paths from PROJECT_ROOT
    return str(Path(p).as_posix()).lstrip("./")

def scan_reflexes() -> list[str]:
    found = []
    if not REFLEX_DIR.exists():
        return found
    for py in REFLEX_DIR.rglob("*.py"):
        if py.name.startswith("__"):
            continue
        if is_reflex_file(py):
            rel = py.relative_to(PROJECT_ROOT).as_posix()
            found.append(rel)
    return sorted(found)

def compare_to_registry(found: list[str], registered: set) -> list[str]:
    missing = []
    for rel in found:
        if rel not in registered:
            missing.append(rel)
    return missing

def run_cli():
    log_trace_event("cli_start", tool="reflex_registry_scanner", required_phase=REQUIRED_PHASE)
    print("🔍 Scanning for active reflex files...")

    found = scan_reflexes()
    print(f"• active_reflex_files_found: {len(found)}")

    registered = load_registry()
    if not registered:
        print("❌ Cannot continue without a valid reflex_registry.json.")
        log_trace_event("cli_end", status="no_registry", required_phase=REQUIRED_PHASE)
        log_memory_event(
            event_type="reflex_registry_scan",
            details={"status": "no_registry", "found": len(found)},
        )
        return

    missing = compare_to_registry(found, registered)

    if missing:
        print("\n⚠️  MISSING reflex registrations:")
        for m in missing:
            print(f"   - {m}")
        print("\n📌 Add these entries to configs/reflex_registry.json (list or dict is fine).")
        status = "missing_entries"
    else:
        print("✅ All reflexes are correctly registered.")
        status = "ok"

    log_trace_event(
        "cli_end",
        status=status,
        found=len(found),
        registered=len(registered),
        missing=len(missing),
        required_phase=REQUIRED_PHASE,
    )
    log_memory_event(
        event_type="reflex_registry_scan",
        details={"status": status, "found": len(found), "registered": len(registered), "missing": missing},
    )

if __name__ == "__main__":
    run_cli()

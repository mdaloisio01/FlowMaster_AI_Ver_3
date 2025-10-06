"""
Auto Phase Guard Fixer — Phase 0.7
Adds the standard path inject + REQUIRED_PHASE guard to files missing it.
Safe to re-run; skips files already guarded.
"""

import os, sys, io, re

REQUIRED_PHASE = "0.7"

HEADER = f"""# === IronRoot Phase Guard (auto-injected) ===
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from boot.boot_path_initializer import inject_paths
inject_paths()
from core.phase_control import ensure_phase
REQUIRED_PHASE = {REQUIRED_PHASE}
ensure_phase(REQUIRED_PHASE)
# === /IronRoot Phase Guard ===

"""

# Exact filenames from your sweep (normalize slashes)
TARGETS = [
"Canonical_Reflex_Template.py",
"_probe_blue_larch.py",
"_probe_canary.py",
"_schema_cols.py",
"_schema_probe.py",
"__init__.py",
"boot/boot_path_initializer.py",
"boot/boot_trace_logger.py",
"boot/__init__.py",
"configs/__init__.py",
"core/memory_interface.py",
"core/memory_log_db.py",
"core/phase_control.py",
"core/snapshot_manager.py",
"core/sqlite_bootstrap.py",
"core/trace_logger.py",
"core/__init__.py",
"sandbox/__init__.py",
"seeds/seed_identity.py",
"seeds/seed_ironroot_summary.py",
"seeds/seed_operator_preferences.py",
"seeds/seed_origin_story.py",
"seeds/__init__.py",
"tests/test_phase_0_2_integrity.py",
"tests/__init__.py",
"core/memory/will_memory_engine.py",
]

GUARD_MARKER = "ensure_phase(REQUIRED_PHASE)"

def needs_guard(text: str) -> bool:
    # if already present, skip
    if GUARD_MARKER in text:
        return False
    # if an alternate guard exists, skip (best-effort)
    if re.search(r"ensure_phase\(\s*[\d\.]+|REQUIRED_PHASE\s*\)", text):
        return False
    return True

def inject_guard(path: str):
    try:
        with io.open(path, "r", encoding="utf-8") as f:
            orig = f.read()
    except (FileNotFoundError, IsADirectoryError):
        return False, "missing"

    # Skip non-.py or already guarded files
    if not path.endswith(".py"):
        return False, "non-py"
    if not needs_guard(orig):
        return False, "present"

    # Keep shebang/encoding lines at top if present
    lines = orig.splitlines(True)
    i = 0
    while i < len(lines) and (lines[i].startswith("#!") or "coding" in lines[i].lower()):
        i += 1
    new_text = "".join(lines[:i]) + HEADER + "".join(lines[i:])

    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(new_text)
    return True, "injected"

def main():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    injected, skipped, missing = [], [], []
    for t in TARGETS:
        full = os.path.join(root, t.replace("/", os.sep))
        ok, status = inject_guard(full)
        if status == "injected":
            injected.append(t)
        elif status == "missing":
            missing.append(t)
        else:
            skipped.append((t, status))
    print(f"Injected: {len(injected)}")
    for f in injected: print(f"  + {f}")
    print(f"Skipped : {len(skipped)}")
    for f, s in skipped: print(f"  - {f} ({s})")
    if missing:
        print(f"Missing : {len(missing)}")
        for f in missing: print(f"  ! {f}")

if __name__ == "__main__":
    main()

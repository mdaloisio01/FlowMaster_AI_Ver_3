#!/usr/bin/env python3
"""
Phase-neutral helper: prints the current phase from configs/ironroot_manifest_data.json
No dependency on boot/*.
"""

from __future__ import annotations
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = REPO_ROOT / "configs" / "ironroot_manifest_data.json"

def get_current_phase() -> str:
    if not MANIFEST.exists():
        print(f"ERROR: Manifest not found at {MANIFEST}", file=sys.stderr)
        sys.exit(2)
    try:
        with MANIFEST.open("r", encoding="utf-8") as f:
            data = json.load(f)
        phase = str(data.get("current_phase", "")).strip()
        if not phase:
            print("ERROR: 'current_phase' missing in manifest.", file=sys.stderr)
            sys.exit(3)
        return phase
    except Exception as e:
        print(f"ERROR: Failed to read manifest: {e}", file=sys.stderr)
        sys.exit(4)

def run_cli(argv: list[str]) -> int:
    phase = get_current_phase()
    print(phase)
    return 0

if __name__ == "__main__":
    sys.exit(run_cli(sys.argv[1:]))

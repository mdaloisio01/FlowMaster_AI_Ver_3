from __future__ import annotations
# boot/boot_path_initializer.py — path setup only (no phase checks)

import os, sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent

def inject_paths() -> None:
    """Idempotently add repo root to sys.path (highest precedence)."""
    p = str(_REPO_ROOT)
    if p not in sys.path:
        sys.path.insert(0, p)

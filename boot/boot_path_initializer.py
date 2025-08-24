# boot/boot_path_initializer.py
# Ensures the project root is on sys.path for reliable imports across tools/reflexes/tests.
# Also installs a global exception hook so uncaught errors are logged.

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional


def _detect_project_root(start: Optional[Path] = None) -> Path:
    """
    Best-effort detection:
      1) Walk up from this file to find configs/ironroot_manifest_data.json
      2) Else the first parent containing both 'boot' and 'core'
      3) Else CWD
    """
    here = (start or Path(__file__)).resolve()
    candidates = [here] + list(here.parents)
    for p in candidates:
        try:
            if (p / "configs" / "ironroot_manifest_data.json").exists():
                return p
            if (p / "boot").is_dir() and (p / "core").is_dir():
                return p
        except Exception:
            continue
    return Path.cwd().resolve()


_PROJECT_ROOT = _detect_project_root()


def inject_paths() -> None:
    """
    Prepend the project root to sys.path if missing.
    Always uses forward slashes in debug prints.
    """
    root = _PROJECT_ROOT
    root_str = root.as_posix()
    # Avoid duplicates; ensure highest priority
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    # Optional env normalization: prefer UTF-8 behavior
    os.environ.setdefault("PYTHONUTF8", "1")


# Install the global exception hook exactly once when this module is imported.
# This guarantees that any CLI/reflex/test that imports boot.boot_path_initializer
# gets automatic error logging for uncaught exceptions.
try:
    # Ensure our project root is importable before hooking (no-op if already present)
    inject_paths()
    from boot.boot_exception_logger import install_global_exception_hook  # type: ignore
    install_global_exception_hook()
except Exception:
    # Never break import just because error logging failed
    pass

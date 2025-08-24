# boot/__init__.py
# Package initializer for the boot module. Kept side-effect free.
# This enables `import boot` and explicit imports from submodules.

from __future__ import annotations

__all__ = [
    "boot_path_initializer",
    "boot_phase_loader",
    "boot_trace_logger",
]

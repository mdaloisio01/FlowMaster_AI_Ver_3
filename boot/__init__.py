from __future__ import annotations
# boot package — minimal init

from .boot_path_initializer import inject_paths  # re-export for tools

__all__ = ["inject_paths"]

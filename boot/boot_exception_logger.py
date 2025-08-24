# boot/boot_exception_logger.py
# Global exception hook that logs uncaught exceptions to both memory and trace.
# - Uses forward-slash paths
# - Stores project-relative sources (handled by the loggers)
# - Idempotent and recursion-safe

from __future__ import annotations

import sys
import traceback
from pathlib import Path
from typing import Optional, Tuple

# We import lazily in the hook to minimize import side-effects, but cache after first call.
_LOGGERS: Tuple[object, object, object] | None = None  # (log_memory_event, log_trace_event, REQUIRED_PHASE)


def _load_loggers() -> Tuple[object, object, object]:
    global _LOGGERS
    if _LOGGERS is not None:
        return _LOGGERS
    # Local imports to avoid circulars at process start
    from core.memory_interface import log_memory_event  # type: ignore
    from core.trace_logger import log_trace_event      # type: ignore
    from core.phase_control import REQUIRED_PHASE      # type: ignore
    _LOGGERS = (log_memory_event, log_trace_event, REQUIRED_PHASE)
    return _LOGGERS


def _classify_tags(src_path: str) -> list[str]:
    p = src_path.replace("\\", "/")
    tags = ["error"]
    if "/tools/" in p:
        tags.insert(0, "tool")
    elif "/reflexes/" in p:
        tags.insert(0, "reflex")
    elif "/tests/" in p:
        tags.insert(0, "test")
    else:
        tags.insert(0, "runtime")
    return tags


def _source_from_tb(tb) -> str:
    try:
        # walk to the last traceback frame (most relevant location)
        last = tb
        while last.tb_next is not None:
            last = last.tb_next
        f = last.tb_frame
        return Path(f.f_code.co_filename).as_posix()
    except Exception:
        # Fallback to argv[0] or this file
        return Path(sys.argv[0]).as_posix() if sys.argv and sys.argv[0] else Path(__file__).as_posix()


def install_global_exception_hook() -> None:
    """
    Install a global excepthook that logs uncaught exceptions.
    Safe to call multiple times.
    """
    if getattr(sys, "_will_exhook_installed", False):
        return
    sys._will_exhook_installed = True

    orig_hook = sys.excepthook

    def _hook(exc_type, exc, tb):
        # prevent recursive logging
        if getattr(sys, "_will_exhook_active", False):
            try:
                if orig_hook:
                    orig_hook(exc_type, exc, tb)
            finally:
                return

        sys._will_exhook_active = True
        try:
            log_memory_event, log_trace_event, REQUIRED_PHASE = _load_loggers()
            src = _source_from_tb(tb)
            tags = _classify_tags(src)

            # Short, friendly traceback tail
            tb_lines = traceback.format_exception(exc_type, exc, tb)
            # Limit lines to keep entries compact
            tail = "".join(tb_lines[-10:]).strip()

            # Memory log
            try:
                log_memory_event(  # type: ignore[attr-defined]
                    event_text=f"uncaught {exc_type.__name__}",
                    source=src,
                    tags=tags,
                    content={
                        "message": str(exc),
                        "trace_tail": tail,
                    },
                    phase=REQUIRED_PHASE,  # type: ignore[name-defined]
                    event_type="error",
                )
            except Exception:
                pass  # never block the process on logging failure

            # Trace log
            try:
                log_trace_event(  # type: ignore[attr-defined]
                    description=f"uncaught {exc_type.__name__}",
                    source=src,
                    tags=tags,
                    content={
                        "message": str(exc),
                        "trace_tail": tail,
                    },
                    phase=REQUIRED_PHASE,  # type: ignore[name-defined]
                )
            except Exception:
                pass

        finally:
            sys._will_exhook_active = False
            # Preserve original behavior: print the traceback to stderr
            try:
                if orig_hook:
                    orig_hook(exc_type, exc, tb)
            except Exception:
                # Last resort: write minimal message
                sys.stderr.write(f"[will-exhook] {exc_type.__name__}: {exc}\n")

    sys.excepthook = _hook

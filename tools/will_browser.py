# /tools/will_browser.py
"""
Will Browser — Phase 0.7 (IronSpine)
Plain talk:
  - Opens ChatGPT inside a WebView2 window.
  - Python (not JS) pulls visible chat text on a timer and on big jumps,
    then POSTS it to http://127.0.0.1:8765/save.
  - Persists login with a user-writable profile folder.

IR compliance:
  - Phase lock: REQUIRED_PHASE = 0.7 with ensure_phase()
  - Dual logging: log_memory_event + log_trace_event on start/inject/save
  - Dispatch-only: capture+POST; storage is handled by your listener+chunker

Run:
  python -m tools.will_browser
(Use your .bat launcher.)
"""

from boot.boot_path_initializer import inject_paths
inject_paths()

import os
import json
import textwrap
import threading
import time
import hashlib
import urllib.request
import urllib.error

import webview  # pip install pywebview

from core.phase_control import ensure_phase, get_current_phase
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event

REQUIRED_PHASE = 0.7
ensure_phase(REQUIRED_PHASE)

# --- Config ---
CHATGPT_URL = "https://chat.openai.com/"
LISTENER_URL = "http://127.0.0.1:8765/save"

AUTOSAVE_SEC = 60              # pull every ~60s
BIG_JUMP_MIN_CHARS = 500       # immediate save if growth >= 500 chars
FORCE_SAVE_SEC = 120           # force a save every ~120s even if no diff

# WebView2 storage (cookies/sessions persist here)
PROFILE_DIR = os.path.join(
    os.environ.get("LOCALAPPDATA", os.getcwd()),
    "WillBrowserProfile"
)

# --- internal state for the Python-side saver ---
_state = {
    "last_len": 0,
    "last_fp": "",
    "last_force": 0,
    "running": True,
}


def _js_get_text() -> str:
    """JS to extract visible chat text from the page (as a single string)."""
    return textwrap.dedent("""
        (function() {
          function root() {
            return document.querySelector('[data-testid="conversation-turns"]')
                   || document.querySelector('main')
                   || document.body;
          }
          const r = root().cloneNode(true);
          const remove = [
            'textarea','input','button','nav','header','footer','form',
            '[role="textbox"]','[data-testid="composer"]','[data-testid="sidebar"]'
          ];
          remove.forEach(sel => r.querySelectorAll(sel).forEach(n => n.remove()));
          const txt = (r.innerText || '')
            .replace(/\\u00A0/g,' ')
            .replace(/\\r\\n/g,'\\n')
            .replace(/\\n{3,}/g,'\\n\\n')
            .trim();
          return txt;
        })();
    """)


def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8", errors="ignore")).hexdigest()


def _post_to_listener(content: str, title: str, url: str, tab_id: str = "will-browser"):
    """POST the bundle to the local listener using stdlib (no requests dep)."""
    payload = {
        "content": content,
        "title": title,
        "url": url,
        "tab_id": tab_id
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        LISTENER_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            _ = resp.read()
        log_trace_event("will_browser_post_ok", source=__file__, phase=REQUIRED_PHASE,
                        tags=["will_browser", "post"], content=f"bytes={len(data)}")
        return True
    except urllib.error.URLError as e:
        log_trace_event("will_browser_post_error", source=__file__, phase=REQUIRED_PHASE,
                        tags=["will_browser", "error"], content=str(e))
        return False


def _poll_and_save_loop(window: webview.Window):
    """
    Background loop:
      - pull text with window.evaluate_js()
      - compare to prior fingerprint/length
      - send on change, big jump, or force interval
    """
    log_trace_event("will_browser_loop_start", source=__file__, phase=REQUIRED_PHASE,
                    tags=["will_browser"])
    _state["last_force"] = time.time()
    while _state["running"]:
        try:
            # Pull text and metadata from the page
            text = window.evaluate_js(_js_get_text()) or ""
            title = window.get_current_url()  # fallback to URL if title fetch below fails
            try:
                # small helper to read document.title
                title_js = "(function(){return document.title || '';})();"
                doc_title = window.evaluate_js(title_js) or ""
                if doc_title:
                    title = doc_title
            except Exception:
                pass
            url_js = "(function(){return location.href || '';})();"
            url = window.evaluate_js(url_js) or ""

            t = text.strip()
            length = len(t)
            fp = _sha256(t) if t else ""

            now = time.time()
            big_jump = abs(length - _state["last_len"]) >= BIG_JUMP_MIN_CHARS
            changed = (fp and fp != _state["last_fp"])
            force_due = (now - _state["last_force"]) >= FORCE_SAVE_SEC

            if (t and (changed or big_jump or force_due)):
                ok = _post_to_listener(t, title=title, url=url)
                if ok:
                    _state["last_len"] = length
                    _state["last_fp"] = fp
                    if force_due:
                        _state["last_force"] = now
                    log_memory_event("will_browser_saved", source=__file__, phase=REQUIRED_PHASE,
                                     tags=["will_browser"], content=f"len={length}")
            # sleep until next pull
            for _ in range(AUTOSAVE_SEC):
                if not _state["running"]:
                    break
                time.sleep(1)
        except Exception as e:
            log_trace_event("will_browser_loop_error", source=__file__, phase=REQUIRED_PHASE,
                            tags=["will_browser", "error"], content=str(e))
            time.sleep(2)  # small backoff


def _on_loaded(window: webview.Window):
    """Start the Python-side saver once the WebView is ready."""
    try:
        # quick no-op inject just to trace readiness
        ok = window.evaluate_js("(function(){return true;})()")
        log_trace_event("will_browser_injected_js", source=__file__, phase=REQUIRED_PHASE,
                        tags=["will_browser", "inject"], content=f"injected_ok={ok}")
    except Exception as e:
        log_trace_event("will_browser_inject_error", source=__file__, phase=REQUIRED_PHASE,
                        tags=["will_browser", "error"], content=str(e))

    # Start the polling thread
    t = threading.Thread(target=_poll_and_save_loop, args=(window,), daemon=True)
    t.start()


def run():
    # Ensure profile dir exists for persistent login
    os.makedirs(PROFILE_DIR, exist_ok=True)

    # Phase + memory trace at boot
    current = get_current_phase()
    log_memory_event("will_browser_start", source=__file__, phase=REQUIRED_PHASE,
                     tags=["will_browser"], content=f"current_phase={current}")
    log_trace_event("will_browser_start", source=__file__, phase=REQUIRED_PHASE,
                    tags=["will_browser"], content=f"url={CHATGPT_URL}")

    # Create the WebView window (storage_path set in start to persist cookies)
    window = webview.create_window(
        title=f"Will Browser — ChatGPT (Phase {REQUIRED_PHASE})",
        url=CHATGPT_URL,
        width=1200,
        height=800,
        resizable=True
    )

    try:
        webview.start(
            _on_loaded,
            window,
            debug=False,
            private_mode=False,
            storage_path=PROFILE_DIR
        )
    finally:
        # shut down loop cleanly
        _state["running"] = False
        log_trace_event("will_browser_exit", source=__file__, phase=REQUIRED_PHASE,
                        tags=["will_browser"])


def run_cli():
    run()


if __name__ == "__main__":
    run_cli()

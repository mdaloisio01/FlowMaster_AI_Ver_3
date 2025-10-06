
# /tools/autosave/local_listener.py
"""
Local Autosave Listener — Phase 0.7
Plain talk:
  - HTTP server on 127.0.0.1 that accepts chat bundles at /save
  - Writes markdown bundles into repo/chat_logs (handled by autosave_helper)
  - Triggers chunker after save
  - **Now CORS-aware** so a browser page (ChatGPT in Will Browser) can POST here.

Run:
  python -m tools.autosave.local_listener --port 8765
"""

from boot.boot_path_initializer import inject_paths
inject_paths()

import argparse
import datetime as dt
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from urllib.parse import urlparse, parse_qs

from core.phase_control import ensure_phase
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event
from tools.autosave.autosave_helper import (
    load_policy,
    write_bundle_md,
    split_into_bundles_by_tokens,
)
from tools.chunker.chunker import run_chunker

REQUIRED_PHASE = 0.7
ensure_phase(REQUIRED_PHASE)

POLICY_PATH = "configs/autosave_policy.json"

# ---------- helpers ----------
def _cors_headers(handler: BaseHTTPRequestHandler):
    # Allow the browser to talk to localhost from https origins
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")

def _json(handler: BaseHTTPRequestHandler, status: int, obj: dict):
    payload = json.dumps(obj).encode("utf-8")
    handler.send_response(status)
    _cors_headers(handler)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(payload)))
    handler.end_headers()
    handler.wfile.write(payload)

def _text(handler: BaseHTTPRequestHandler, status: int, text: str):
    data = text.encode("utf-8")
    handler.send_response(status)
    _cors_headers(handler)
    handler.send_header("Content-Type", "text/plain; charset=utf-8")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)

# ---------- request handler ----------
class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        # quieter default logging; print minimal line
        print(f"{self.address_string()} - {fmt % args}")

    def do_OPTIONS(self):
        # CORS preflight
        self.send_response(204)  # No Content
        _cors_headers(self)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            _json(self, 200, {"status": "ok", "phase": REQUIRED_PHASE})
            return
        _text(self, 404, "not found")

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/save":
            _text(self, 404, "not found")
            return

        # read body
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(raw.decode("utf-8"))
        except Exception:
            _json(self, 400, {"error": "invalid json"})
            return

        content = (data.get("content") or "").strip()
        title = data.get("title")
        url = data.get("url")
        tab_id = data.get("tab_id")

        if not content:
            _json(self, 400, {"error": "empty content"})
            return

        # load autosave policy & prep paths
        policy = load_policy(POLICY_PATH)
        chat_logs_dir = policy["paths"]["chat_logs_dir"]
        os.makedirs(chat_logs_dir, exist_ok=True)

        # write one bundle file (we let autosave_helper handle YAML etc.)
        date_str = dt.date.today().isoformat()
        bundles = split_into_bundles_by_tokens(content, policy["autosave"]["bundle_token_limit"])

        # choose a simple topic (fall back to title/url if needed)
        topic = title or (url or "ChatGPT").split("/")[2]
        seq = "cp-01"  # listener writes one file per call; autosave_helper rotates in its own loop

        # compose filename safely
        from tools.autosave.autosave_helper import slugify, make_filename
        out_path = make_filename(chat_logs_dir, date_str, topic, seq)

        # write bundle (single chunk for listener POST; count tokens already done)
        token_est = 0
        if bundles:
            bundle_text, token_est = bundles[0]
        else:
            bundle_text = content

        write_bundle_md(
            out_path,
            bundle_text,
            topic=topic,
            phase=REQUIRED_PHASE,
            source_title=title,
            source_url=url,
            tab_id=tab_id,
            seq=seq,
            token_estimate=token_est,
        )

        # logs
        log_memory_event("listener_saved_bundle", source=__file__, phase=REQUIRED_PHASE,
                         tags=["autosave","listener"], content=f"path={out_path}")
        log_trace_event("listener_saved_bundle", source=__file__, phase=REQUIRED_PHASE,
                        tags=["autosave","listener"], content=f"path={out_path}")

        # run chunker after save
        if policy["post_save_actions"].get("run_chunker", True):
            run_chunker(policy["paths"]["chunker_input_root"], write_txt=policy["post_save_actions"].get("export_txt_chunks", True))

        _json(self, 200, {"status": "saved", "path": out_path})

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

# ---------- CLI ----------
def run_cli():
    parser = argparse.ArgumentParser(description="Local Autosave Listener (CORS-enabled)")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    srv = ThreadedHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"🟢 Autosave listener running at http://127.0.0.1:{args.port}  (GET /health, POST /save)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n⏹ Stopped.")

if __name__ == "__main__":
    run_cli()

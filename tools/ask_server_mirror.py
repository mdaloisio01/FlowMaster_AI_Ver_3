# /tools/ask_server_mirror.py
# Same API as ask_server, but also appends each Q/A to repo\chat_logs\<date>__willchat__cp-01.txt

from boot.boot_path_initializer import inject_paths; inject_paths()
from http.server import BaseHTTPRequestHandler, HTTPServer
import json, os, datetime

from core.phase_control import ensure_phase
REQUIRED_PHASE = 0.7
ensure_phase(REQUIRED_PHASE)

from tools import ask_will  # after path inject

HOST, PORT = "127.0.0.1", 8766  # same port as your current page expects

LOG_DIR = os.path.join("repo", "chat_logs")
os.makedirs(LOG_DIR, exist_ok=True)

def _log_willchat(q: str, res: dict):
    """Append a compact entry to today's willchat log file."""
    date = datetime.date.today().strftime("%Y-%m-%d")
    path = os.path.join(LOG_DIR, f"{date}__willchat__cp-01.txt")
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ans = (res.get("answer") or "").replace("\r", "").strip()
    # keep the file small & parseable
    if len(ans) > 1200:
        ans = ans[:1200] + " …"
    sources = res.get("sources") or []
    src_lines = [f"{s['file_path']}#chunk-{s['chunk_index']}" for s in sources]
    block = (
        f"[{ts}] Q: {q}\n"
        f"A: {ans}\n"
        f"Sources: " + (", ".join(src_lines) if src_lines else "(none)") + "\n"
        "----\n"
    )
    with open(path, "a", encoding="utf-8") as f:
        f.write(block)

class Handler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200, ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "content-type")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS, GET")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(204)

    def do_GET(self):
        if self.path.startswith("/health"):
            self._set_headers(200)
            self.wfile.write(json.dumps({"ok": True, "phase": REQUIRED_PHASE}).encode("utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error":"not found"}')

    def do_POST(self):
        if self.path != "/ask":
            self._set_headers(404)
            self.wfile.write(b'{"error":"not found"}')
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length) if length > 0 else b"{}"
            body = json.loads(raw.decode("utf-8", errors="replace"))
            q = str(body.get("q", "")).strip()
            k = int(body.get("k", 5))
            if not q:
                self._set_headers(400)
                self.wfile.write(b'{"error":"missing q"}')
                return

            res = ask_will.ask(q, k=k)
            # mirror-log to repo/chat_logs
            try:
                _log_willchat(q, res)
            except Exception as e:
                # don't fail the request if logging has an issue
                pass

            self._set_headers(200)
            self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

def run():
    srv = HTTPServer((HOST, PORT), Handler)
    print(f"Will ask server (mirror) listening on http://{HOST}:{PORT}")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()

if __name__ == "__main__":
    run()

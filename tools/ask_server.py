# Minimal JSON server: POST /ask {"q": "..."} -> Will's answer + sources.
# No external deps; uses built-in http.server.

from boot.boot_path_initializer import inject_paths; inject_paths()
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

from core.phase_control import ensure_phase
REQUIRED_PHASE = 0.7
ensure_phase(REQUIRED_PHASE)

# Import after path injection
from tools import ask_will

HOST, PORT = "127.0.0.1", 8766

class Handler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200, ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")   # local use
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
            if not q:
                self._set_headers(400)
                self.wfile.write(b'{"error":"missing q"}')
                return

            res = ask_will.ask(q, k=int(body.get("k", 5)))
            self._set_headers(200)
            self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

def run():
    srv = HTTPServer((HOST, PORT), Handler)
    print(f"Will ask server listening on http://{HOST}:{PORT}")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()

if __name__ == "__main__":
    run()

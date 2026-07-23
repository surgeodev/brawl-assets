#!/usr/bin/env python3
"""Simple daemon server - runs until killed."""
import http.server, json, subprocess, sys, os
from pathlib import Path

BASE = Path(__file__).parent.resolve()
PORT = int(os.environ.get("PORT", 8080))

class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(BASE), **kw)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode() if length else ""
        if self.path == "/api/add-example":
            try:
                data = json.loads(body) if body else {}
                url = data.get("url", "")
                if not url:
                    self.send_json(400, {"error": "Missing url"})
                    return
                r = subprocess.run(
                    [sys.executable, str(BASE / "scripts" / "youtube_example.py"), url],
                    capture_output=True, text=True, timeout=60,
                )
                if r.returncode == 0:
                    self.send_json(200, {"ok": True})
                else:
                    self.send_json(500, {"error": r.stderr or r.stdout})
            except Exception as e:
                self.send_json(500, {"error": str(e)})
        elif self.path == "/api/trigger-scrape":
            try:
                r = subprocess.run(
                    ["gh", "workflow", "run", "update.yml", "--repo", "surgeodev/brawl-assets"],
                    capture_output=True, text=True, timeout=30,
                )
                if r.returncode == 0:
                    self.send_json(200, {"ok": True, "url": r.stdout.strip()})
                else:
                    self.send_json(500, {"error": r.stderr or r.stdout})
            except Exception as e:
                self.send_json(500, {"error": str(e)})
        elif self.path == "/api/pull":
            try:
                r = subprocess.run(
                    ["git", "pull"],
                    capture_output=True, text=True, timeout=60, cwd=str(BASE),
                )
                if r.returncode == 0:
                    self.send_json(200, {"ok": True, "output": r.stdout})
                else:
                    self.send_json(500, {"error": r.stderr or r.stdout})
            except Exception as e:
                self.send_json(500, {"error": str(e)})
        else:
            self.send_json(404, {"error": "not found"})

    def send_json(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, fmt, *a):
        sys.stderr.write(f"[server] {fmt % a}\n")


httpd = http.server.HTTPServer(("0.0.0.0", PORT), H)
print(f"Serving on http://0.0.0.0:{PORT}", flush=True)
httpd.serve_forever()

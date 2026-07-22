#!/bin/bash
# Start the Brawl Assets Hub server
# Usage: bash start_server.sh [port]

PORT=${1:-8080}
cd "$(dirname "$0")"

echo "Starting Brawl Assets Hub on http://localhost:$PORT"
echo "API: POST /api/add-example with {\"url\": \"...\"}"
echo "Press Ctrl+C to stop"
echo ""

exec python3 -c "
import http.server, json, subprocess, sys
from pathlib import Path

BASE = Path('.')
PORT = $PORT

class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(BASE), **kw)
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode() if length else ''
        if self.path == '/api/add-example':
            try:
                data = json.loads(body) if body else {}
                url = data.get('url', '')
                if not url:
                    self.send(400, {'error':'Missing url'}); return
                r = subprocess.run([sys.executable, 'scripts/youtube_example.py', url], capture_output=True, text=True, timeout=60)
                if r.returncode == 0:
                    self.send(200, {'ok':True, 'output':r.stdout})
                else:
                    self.send(500, {'error':r.stderr or r.stdout})
            except Exception as e:
                self.send(500, {'error':str(e)})
        else:
            self.send(404, {'error':'not found'})
    def send(self, code, data):
        self.send_response(code)
        self.send_header('Content-Type','application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

httpd = http.server.HTTPServer(('0.0.0.0', PORT), H)
print(f'Server on http://localhost:{PORT}')
httpd.serve_forever()
"

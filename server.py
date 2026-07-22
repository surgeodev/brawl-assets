#!/usr/bin/env python3
"""Brawl Assets Hub — local server with YouTube example download API."""
import http.server
import json
import os
import re
import subprocess
import urllib.parse
from pathlib import Path

BASE = Path(__file__).parent.resolve()
PORT = 8080

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE), **kwargs)

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode() if length else ''

        if self.path == '/api/add-example':
            try:
                data = json.loads(body) if body else {}
                url = data.get('url', '')
                if not url:
                    self.send_json(400, {'error': 'Missing url'})
                    return

                result = subprocess.run(
                    [sys.executable, str(BASE / 'scripts' / 'youtube_example.py'), url],
                    capture_output=True, text=True, timeout=60
                )

                if result.returncode == 0:
                    self.send_json(200, {'ok': True, 'output': result.stdout})
                else:
                    self.send_json(500, {'error': result.stderr or result.stdout})
            except Exception as e:
                self.send_json(500, {'error': str(e)})
        else:
            self.send_json(404, {'error': 'not found'})

    def send_json(self, code, data):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

if __name__ == '__main__':
    import sys
    httpd = http.server.HTTPServer(('0.0.0.0', PORT), Handler)
    print(f"🌐 Brawl Assets Hub → http://localhost:{PORT}")
    print(f"   (API endpoint: POST /api/add-example with {\"url\": \"...\"})")
    httpd.serve_forever()

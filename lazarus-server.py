#!/usr/bin/env python3
"""
Project Lazarus — Desktop Server
Serves Lazarus.html and proxies /osc/* requests to the Gear 360 camera.
Adds COOP/COEP headers for SharedArrayBuffer (Video Lab) support.

Usage:
  python3 lazarus-server.py
  Then open http://localhost:8080
"""

import http.server
import urllib.request
import urllib.error
import json
import os
import sys

CAMERA_IP = "192.168.107.1"
PORT = 8080
HTML_FILE = "Lazarus.html"


class LazarusHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        if self.path.startswith("/osc/"):
            self._proxy("GET")
        elif self.path == "/" or self.path == "/index.html":
            self._serve_html()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.startswith("/osc/"):
            self._proxy("POST")
        else:
            self.send_error(404)

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def _serve_html(self):
        for name in [HTML_FILE, "index.html"]:
            if os.path.exists(name):
                self.path = "/" + name
                # Inject COOP/COEP headers for SharedArrayBuffer
                with open(name, 'rb') as f:
                    content = f.read()
                self.send_response(200)
                self._cors()
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", len(content))
                self.end_headers()
                self.wfile.write(content)
                return
        self.send_error(404, "Lazarus.html not found in current directory")

    def _proxy(self, method):
        url = f"http://{CAMERA_IP}{self.path}"
        try:
            body = None
            if method == "POST":
                length = int(self.headers.get("Content-Length", 0))
                if length > 0:
                    body = self.rfile.read(length)

            req = urllib.request.Request(url, data=body, method=method)
            req.add_header("Content-Type", "application/json")

            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
                self.send_response(resp.status)
                self._cors()
                self.send_header("Content-Type", resp.headers.get("Content-Type", "application/json"))
                self.send_header("Content-Length", len(data))
                self.end_headers()
                self.wfile.write(data)

        except urllib.error.URLError as e:
            msg = json.dumps({"error": f"Camera unreachable: {e.reason}"})
            self.send_response(502)
            self._cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(msg.encode())

        except Exception as e:
            msg = json.dumps({"error": str(e)})
            self.send_response(500)
            self._cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(msg.encode())

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")

    def log_message(self, fmt, *args):
        path = args[0] if args else ""
        if "/osc/" in str(path):
            sys.stdout.write(f"  📡 {path}\n")
        elif "GET / " in str(path) or "Lazarus" in str(path):
            sys.stdout.write(f"  🌐 {path}\n")


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)) or ".")

    if not os.path.exists(HTML_FILE) and not os.path.exists("index.html"):
        print(f"\n  ⚠  {HTML_FILE} not found in {os.getcwd()}")
        print(f"     Put {HTML_FILE} in the same folder as this script.\n")
        sys.exit(1)

    print()
    print("  ┌─────────────────────────────────────────┐")
    print("  │     PROJECT LAZARUS — Desktop Server     │")
    print("  ├─────────────────────────────────────────┤")
    print(f"  │  Open:   http://localhost:{PORT}          │")
    print(f"  │  Camera: {CAMERA_IP}               │")
    print("  │                                         │")
    print("  │  Press Ctrl+C to stop                   │")
    print("  └─────────────────────────────────────────┘")
    print()

    server = http.server.HTTPServer(("0.0.0.0", PORT), LazarusHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
        server.server_close()

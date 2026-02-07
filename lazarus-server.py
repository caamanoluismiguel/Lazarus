#!/usr/bin/env python3
"""
Project Lazarus v3.1 — Desktop Server
Proxies ALL camera traffic: OSC API, image downloads, live preview.

v3.0 bug: Only proxied /osc/* — image downloads returned 404.
v3.1 fix: Proxies /osc/*, /DCIM/*, /thumb/*, any .jpg/.mp4 to camera.
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

# Paths forwarded to camera
CAMERA_PREFIXES = ("/osc/", "/DCIM/", "/dcim/", "/thumb/", "/live")


class LazarusHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        if self._is_camera_path(self.path):
            self._proxy("GET")
        elif self.path == "/" or self.path == "/index.html":
            self._serve_html()
        else:
            super().do_GET()

    def do_POST(self):
        if self._is_camera_path(self.path):
            self._proxy("POST")
        else:
            self.send_error(404)

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def _is_camera_path(self, path):
        for prefix in CAMERA_PREFIXES:
            if path.startswith(prefix):
                return True
        # Proxy image/video requests that don't exist locally
        lower = path.lower()
        if any(lower.endswith(ext) for ext in ('.jpg','.jpeg','.mp4','.dng','.raw')):
            if not os.path.exists(path.lstrip('/')):
                return True
        return False

    def _serve_html(self):
        for name in [HTML_FILE, "index.html"]:
            if os.path.exists(name):
                with open(name, 'rb') as f:
                    content = f.read()
                self.send_response(200)
                self._cors()
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", len(content))
                self.end_headers()
                self.wfile.write(content)
                return
        self.send_error(404, "Lazarus.html not found")

    def _proxy(self, method):
        url = f"http://{CAMERA_IP}{self.path}"
        try:
            body = None
            if method == "POST":
                length = int(self.headers.get("Content-Length", 0))
                if length > 0:
                    body = self.rfile.read(length)

            req = urllib.request.Request(url, data=body, method=method)
            ct = self.headers.get("Content-Type")
            if ct:
                req.add_header("Content-Type", ct)
            elif method == "POST":
                req.add_header("Content-Type", "application/json")

            # Longer timeout for media downloads
            timeout = 60 if self._is_media(self.path) else 15

            with urllib.request.urlopen(req, timeout=timeout) as resp:
                resp_ct = resp.headers.get("Content-Type", "application/octet-stream")

                # MJPEG stream (live preview) — stream it through
                if "multipart" in resp_ct:
                    self.send_response(200)
                    self._cors()
                    self.send_header("Content-Type", resp_ct)
                    self.send_header("Cache-Control", "no-cache")
                    self.end_headers()
                    try:
                        while True:
                            chunk = resp.read(8192)
                            if not chunk:
                                break
                            self.wfile.write(chunk)
                            self.wfile.flush()
                    except (BrokenPipeError, ConnectionResetError):
                        pass
                    return

                # Regular response
                data = resp.read()
                self.send_response(resp.status)
                self._cors()
                self.send_header("Content-Type", resp_ct)
                self.send_header("Content-Length", len(data))
                self.end_headers()
                self.wfile.write(data)

        except urllib.error.HTTPError as e:
            # Camera returned an HTTP error — forward it
            try:
                err_body = e.read()
            except:
                err_body = json.dumps({"error": str(e)}).encode()
            self.send_response(e.code)
            self._cors()
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", len(err_body))
            self.end_headers()
            self.wfile.write(err_body)

        except urllib.error.URLError as e:
            reason = str(getattr(e, 'reason', e))
            msg = json.dumps({"error": f"Camera unreachable: {reason}"}).encode()
            self.send_response(502)
            self._cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(msg)

        except Exception as e:
            msg = json.dumps({"error": str(e)}).encode()
            self.send_response(500)
            self._cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(msg)

    def _is_media(self, path):
        lower = path.lower()
        return any(lower.endswith(e) for e in ('.jpg','.jpeg','.mp4')) or '/DCIM/' in path

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")

    def log_message(self, fmt, *args):
        p = str(args[0]) if args else ""
        if "/osc/" in p:
            sys.stdout.write(f"  📡 {p}\n")
        elif "/DCIM/" in p or ".jpg" in p.lower() or ".mp4" in p.lower():
            sys.stdout.write(f"  📸 {p}\n")
        elif "/live" in p:
            sys.stdout.write(f"  🔴 LIVE STREAM\n")
        elif "Lazarus" in p or "GET / " in p:
            sys.stdout.write(f"  🌐 {p}\n")


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)) or ".")

    if not os.path.exists(HTML_FILE) and not os.path.exists("index.html"):
        print(f"\n  ⚠  {HTML_FILE} not found in {os.getcwd()}")
        sys.exit(1)

    print()
    print("  ┌─────────────────────────────────────────┐")
    print("  │     PROJECT LAZARUS v3.1 — Server        │")
    print("  ├─────────────────────────────────────────┤")
    print(f"  │  App:    http://localhost:{PORT}          │")
    print(f"  │  Camera: {CAMERA_IP}               │")
    print("  │                                         │")
    print("  │  Proxies: /osc/* /DCIM/* /live/*         │")
    print("  │  Ctrl+C to stop                         │")
    print("  └─────────────────────────────────────────┘")
    print()

    server = http.server.HTTPServer(("0.0.0.0", PORT), LazarusHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
        server.server_close()

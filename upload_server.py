#!/usr/bin/env python3
"""Minimal HLX upload receiver. Saves files to /uploads with a timestamp prefix."""
import cgi
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

UPLOAD_DIR = os.environ.get('UPLOAD_DIR', '/uploads')
PORT       = 3000
MAX_BYTES  = 5 * 1024 * 1024  # 5 MB

os.makedirs(UPLOAD_DIR, exist_ok=True)

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        if self.path != '/api/upload':
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get('Content-Length', 0))
        if length > MAX_BYTES:
            self.send_response(413)
            self.end_headers()
            return

        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': self.headers['Content-Type']},
        )
        item = form.getvalue('file')
        if item is None:
            self.send_response(400)
            self.end_headers()
            return

        raw = item if isinstance(item, bytes) else item.encode()
        name = (form['file'].filename or 'unknown.hlx').replace('/', '_').replace('\\', '_')
        ts   = int(time.time())
        dest = os.path.join(UPLOAD_DIR, f'{ts}_{name}')
        with open(dest, 'wb') as f:
            f.write(raw)

        self.send_response(200)
        self.end_headers()

if __name__ == '__main__':
    server = HTTPServer(('127.0.0.1', PORT), Handler)
    print(f'Upload server listening on 127.0.0.1:{PORT}', flush=True)
    server.serve_forever()

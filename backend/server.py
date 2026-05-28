#!/usr/bin/env python3
"""Minimal HLX upload receiver. Saves files to /uploads with a timestamp prefix."""
import cgi
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

UPLOAD_DIR = os.environ.get('UPLOAD_DIR', '/uploads')
PORT       = int(os.environ.get('PORT', '3000'))
MAX_BYTES  = 5 * 1024 * 1024  # 5 MB

os.makedirs(UPLOAD_DIR, exist_ok=True)

CORS = {
    'Access-Control-Allow-Origin':  '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
}

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # silence default access log

    def send_cors(self, status=200, body=b'', content_type='text/plain'):
        self.send_response(status)
        for k, v in CORS.items():
            self.send_header(k, v)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_cors()

    def do_POST(self):
        if self.path != '/api/upload':
            self.send_cors(404, b'Not found')
            return

        length = int(self.headers.get('Content-Length', 0))
        if length > MAX_BYTES:
            self.send_cors(413, b'File too large')
            return

        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': self.headers['Content-Type']},
        )
        item = form.getvalue('file')
        if item is None:
            self.send_cors(400, b'No file field')
            return

        raw = item if isinstance(item, bytes) else item.encode()
        name = (form['file'].filename or 'unknown.hlx').replace('/', '_').replace('\\', '_')
        ts   = int(time.time())
        dest = os.path.join(UPLOAD_DIR, f'{ts}_{name}')
        with open(dest, 'wb') as f:
            f.write(raw)

        self.send_cors(200, b'OK')

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', PORT), Handler)
    print(f'Upload server listening on :{PORT}', flush=True)
    server.serve_forever()

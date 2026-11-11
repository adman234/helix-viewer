#!/usr/bin/env python3
"""Minimal HLX upload receiver. Saves files to /uploads with a timestamp prefix."""
import os
import time
from email.parser import BytesParser
from email.policy import HTTP
from http.server import BaseHTTPRequestHandler, HTTPServer

UPLOAD_DIR = os.environ.get('UPLOAD_DIR', '/uploads')
PORT       = 3000
MAX_BYTES  = 5 * 1024 * 1024  # 5 MB

os.makedirs(UPLOAD_DIR, exist_ok=True)


def parse_file_field(content_type, body, field='file'):
    """Return (filename, bytes) for a multipart/form-data field, or None.

    Uses the email package because the cgi module was removed in Python 3.13.
    """
    if not content_type or not content_type.startswith('multipart/form-data'):
        return None
    msg = BytesParser(policy=HTTP).parsebytes(
        b'Content-Type: ' + content_type.encode('latin-1') + b'\r\n\r\n' + body)
    for part in msg.iter_parts():
        if part.get_param('name', header='content-disposition') == field:
            return part.get_filename(), part.get_payload(decode=True) or b''
    return None

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

        body = self.rfile.read(length)
        field = parse_file_field(self.headers.get('Content-Type'), body)
        if field is None:
            self.send_response(400)
            self.end_headers()
            return

        filename, raw = field
        name = (filename or 'unknown.hlx').replace('/', '_').replace('\\', '_')
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

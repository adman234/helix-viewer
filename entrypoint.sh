#!/bin/sh
mkdir -p /uploads
python3 /usr/local/bin/upload_server.py &
exec nginx -g 'daemon off;'

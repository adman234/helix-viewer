FROM nginx:alpine

LABEL description="Line 6 Helix Preset Visualizer"

RUN apk add --no-cache python3

COPY html/ /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY upload_server.py /usr/local/bin/upload_server.py
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

CMD ["/entrypoint.sh"]

FROM nginx:1.27-alpine

RUN rm -f /etc/nginx/conf.d/default.conf \
    && adduser -D -u 1000 appuser

COPY nginx.conf /etc/nginx/nginx.conf
COPY public /usr/share/nginx/html

RUN chown -R appuser:appuser /usr/share/nginx/html /var/cache/nginx

USER appuser

EXPOSE 8080

HEALTHCHECK --interval=10s --timeout=5s --retries=5 --start-period=5s \
  CMD wget -q -O /dev/null http://127.0.0.1:8080/ || exit 1

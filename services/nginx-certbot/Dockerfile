FROM nginx:1.19.6-alpine

RUN apk add --no-cache --update \
    bash curl \
    certbot certbot-nginx \
    busybox-initscripts \
    && rm -rf /var/cache/apk/*

COPY ./config/renew-cert-cron /etc/cron.d/renew-cert-cron
RUN cat /etc/cron.d/renew-cert-cron >> /etc/crontabs/root

COPY ./config/ssl-options/options-ssl-nginx.conf /etc/nginx-conf/ssl-options/options-ssl-nginx.conf
COPY ./entrypoint.sh /var/entrypoint.sh
COPY ./config/templates/ /etc/nginx/templates/

# override the entrypoint to first start cron, then nginx
# ENTRYPOINT [ "/var/entrypoint.sh" ]

# apparently the CMD gets wiped when you set ENTRYPOINT, so we
# re-set it here
# CMD ["nginx", "-g", "daemon off;"]

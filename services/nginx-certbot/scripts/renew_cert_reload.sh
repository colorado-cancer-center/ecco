#!/bin/bash

# This script is used to renew the certificate and reload nginx

certbot certonly \
    --nginx --non-interactive --agree-tos \
    --email ${ADMIN_EMAIL} --domain ${DOMAIN_NAME} && \
nginx -s reload

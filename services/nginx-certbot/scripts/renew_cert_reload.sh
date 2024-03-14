#!/bin/bash

# This script is used to renew the certificate and reload nginx

# if we received more than one space-delimited domain name,
# each of them becomes a '--domain <X>' argument; we end up
# with a cert that can answer for any of them
DOMAIN_ARGS=$( echo "${DOMAIN_NAMES}" | xargs -n 1 echo --domain | paste -sd ' ' )

certbot certonly \
    --nginx --non-interactive --agree-tos \
    --email ${ADMIN_EMAIL} ${DOMAIN_ARGS} --expand && \
nginx -s reload

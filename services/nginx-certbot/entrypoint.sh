#!/bin/bash

# used by, e.g., nginx to find the certs, since the first name in
# the list of domains is used to name the cert folder
export PRIMARY_DOMAIN=$(echo $DOMAIN_NAMES | cut -d' ' -f1)

cron && /docker-entrypoint.sh "$@"

#!/bin/bash

export PRIMARY_DOMAIN=$(echo $DOMAIN_NAME | cut -d' ' -f1)

cron && /docker-entrypoint.sh "$@"

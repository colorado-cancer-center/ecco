#!/usr/bin/env bash

# since pg_isready can succeed even before the db is actually ready,
# we'll require multiple successes for it to be considered healthy

if [ -f /tmp/initialized ]; then
    echo "* Database has already been initialized, skipping healthcheck"
    exit 0
fi

PG_READY_CMD="pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DATABASE}"

( ${PG_READY_CMD} && sleep 10 && ${PG_READY_CMD} ) || exit 1

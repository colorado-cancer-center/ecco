#!/usr/bin/env bash

# since pg_isready can succeed even before the db is actually ready,
# we'll require multiple successes for it to be considered healthy

if [ -f /tmp/initialized ]; then
    echo "* Database has already been initialized, skipping healthcheck"
    exit 0
fi

PG_READY_CMD="pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DATABASE}"

# check that the database is accessible at all, with a 2-second
# sleep to reduce the possibility of a start-and-stop causing
# a false positive
( ${PG_READY_CMD} && sleep 2 && ${PG_READY_CMD} ) || exit 1

# poll for the existence of /tmp/initialized, which is created
# in the patched-entrypoint.sh script after the database is initialized
# and a dump has been loaded.
# if it doesn't exist, the database is not ready
# attempt to check it 5 times, with a 5 second sleep in between
for i in {1..5}; do
    if [ -f /tmp/initialized ]; then
        echo "* Database is ready"
        exit 0
    fi
    sleep 5
done

# presumably the database is not ready
exit 1

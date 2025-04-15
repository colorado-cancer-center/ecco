#!/usr/bin/env bash

# patched-entrypoint.sh writes a file called /tmp/initialized
# to indicate that the database has been fully initialized;
# this includes loading the most recent dump, which can take
# some time.

# our healthcheck script watches for the creation of this
# sentinel file before it proceeds

if [ -f /tmp/initialized ]; then
    echo "* Database has already been initialized, skipping healthcheck"
    exit 0
fi

# poll for the existence of /tmp/initialized
# check up to 10 times every 5 seconds
for i in {1..10}; do
    if [ -f /tmp/initialized ]; then
        echo "* Database is ready"
        exit 0
    fi
    sleep 5
done

# presumably the database is not ready
exit 1

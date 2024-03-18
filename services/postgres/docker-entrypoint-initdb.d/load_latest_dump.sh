#!/bin/bash

if [ -d "/db-exports/" ]; then
    # find the most recent database dump /db-exports/*.dump in by using sort;
    # presumes that dumpfiles are named <label>_<timestamp>.dump
    TARGET_DUMPFILE=$(ls /db-exports/*.dump | sort -t '_' -k2 -r | head -n 1)
    
    echo "* Found db export ${TARGET_DUMPFILE}"

    # drop and recreate the database
    dropdb ${POSTGRES_DATABASE}
    createdb -T template0 ${POSTGRES_DATABASE}
    pg_restore -U ${POSTGRES_USER} -d ${POSTGRES_DATABASE} "${TARGET_DUMPFILE}"

    echo "* Restored db export ${TARGET_DUMPFILE}"
else    
    echo "No db-exports directory found, skipping import"
fi

touch /tmp/initialized

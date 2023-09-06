#!/bin/bash

if [ -d "/db-exports/" ]; then
    # identify the most recent export
    TARGET_DUMPFILE=$( ls -t /db-exports/*.dump | head -n1 )
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

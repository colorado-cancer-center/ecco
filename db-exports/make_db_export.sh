#!/usr/bin/env bash

# this script is used to make a database export, and should be run from
# within the 'db' container

TARGET_DUMPFILE="${POSTGRES_DATABASE}_$( date +%Y-%m-%d).dump"

if [ -f ${TARGET_DUMPFILE} ]; then
    if  [ ${FORCE_OVERWRITE} -ne 1 ]; then
        echo "* File ${TARGET_DUMPFILE} already exists, overwrite it?"
        read -p "  (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "* Aborting"
            exit 1
        fi
    else
        echo "* Overwriting existing file ${TARGET_DUMPFILE}"
    fi
fi

pg_dump -F c -U ${POSTGRES_USER} -d ${POSTGRES_DATABASE} > ${TARGET_DUMPFILE} \
    && echo "* Created db export ${TARGET_DUMPFILE}" \
    || echo "* Failed to create db export (code: $?)"

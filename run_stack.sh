#!/usr/bin/env bash

if [ "$#" -gt 0 ]; then
    ARGS="$@"
else
    ARGS="up --build"
fi

docker compose ${ARGS}

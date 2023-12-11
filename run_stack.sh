#!/usr/bin/env bash

# first, resolve the target environment
# 'dev' is the default
TARGET_ENV="dev"
COMPOSE_FILES=( "docker-compose.yml" "docker-compose.override.yml" )
DEFAULT_ARGS="up --build"

case "$1" in
    "prod")
        TARGET_ENV="prod"
        COMPOSE_FILES=( "docker-compose.yml" "docker-compose.prod.yml" )
        DEFAULT_ARGS="up --build -d"
        shift
        ;;
    "dev")
        # remove the arg, allow this to fall through to base case
        shift
        ;&
    *)
        echo "${1} not recognized as a target env, ignoring"
        ;;
esac

echo "* Using target environment ${TARGET_ENV}"

COMPOSE_FILE_ARGS=$( echo ${COMPOSE_FILES[@]} | xargs -n 1 echo "-f" | xargs )

if [ "$#" -gt 0 ]; then
    ARGS="$@"
else
    ARGS="${DEFAULT_ARGS}"
fi

FINAL_CMD="docker compose ${COMPOSE_FILE_ARGS} ${ARGS}"

echo "* Running command: ${FINAL_CMD}"
${FINAL_CMD}

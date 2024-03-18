#!/usr/bin/env bash

# first, resolve the target environment
# 'dev' is the default
CHOSEN_ENV="dev"
COMPOSE_FILES=( "docker-compose.yml" "docker-compose.override.yml" )
DEFAULT_ARGS="up --build"

# on prod machine, always target prod
if [ $( hostname ) = 'ecco' ]; then
	CHOSEN_ENV="prod"
fi

case "${1:-$CHOSEN_ENV}" in
    "prod")
        TARGET_ENV="prod"
        COMPOSE_FILES=( "docker-compose.yml" "docker-compose.prod.yml" )
        DEFAULT_ARGS="up --build -d"
        shift
        ;;
    "dev")
        # remove the arg, allow this to fall through to base case
        TARGET_ENV="dev"
        shift
        ;;
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

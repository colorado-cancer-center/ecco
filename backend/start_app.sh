#!/usr/bin/env bash

IS_DEV=${IS_DEV:-0}

APP_HOST="0.0.0.0"
APP_PORT="8000"

# import counties
ogr2ogr -f "PostgreSQL" PG:"host=${POSTGRES_HOST} dbname=${POSTGRES_DATABASE} user=${POSTGRES_USER} password=${POSTGRES_PASSWORD}" \
    /data/geometry/Colorado_County_Boundaries.geojson \
    -nln county -overwrite

# import tracts
ogr2ogr -f "PostgreSQL" PG:"host=${POSTGRES_HOST} dbname=${POSTGRES_DATABASE} user=${POSTGRES_USER} password=${POSTGRES_PASSWORD}" \
    /data/geometry/Colorado_Census_Tract_Boundaries.geojson \
    -nln tract -overwrite

# apply migrations at startup
alembic upgrade head

# load up CO county boundaries from reference data
# ogr2ogr -f "PostgreSQL" PG:"host=${POSTGRES_HOST} dbname=${POSTGRES_DATABASE} user=${POSTGRES_USER} password=${POSTGRES_PASSWORD}" \
#     /data/geometry/Colorado_County_Boundaries.geojson \
#     -nln co_county_boundaries -overwrite

# note that alembic must have already created the county and tract tables
# for the imports below to work

if [ "${IS_DEV}" = "1" ]; then
    uvicorn main:app --reload --host "${APP_HOST}" --port "${APP_PORT}"
else
    uvicorn main:app --host "${APP_HOST}" --port "${APP_PORT}"
fi

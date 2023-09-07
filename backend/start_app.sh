#!/usr/bin/env bash

IS_DEV=${IS_DEV:-0}

APP_HOST="0.0.0.0"
APP_PORT="8000"

# if 1, uses high-resolution tracts, but at the cost of higher memory/data usage
USE_HIGH_RES_TRACTS=${USE_HIGH_RES_TRACTS:-0}


# ========================================
# === geometry import via ogr2ogr
# ========================================

# import counties
ogr2ogr -f "PostgreSQL" PG:"host=${POSTGRES_HOST} dbname=${POSTGRES_DATABASE} user=${POSTGRES_USER} password=${POSTGRES_PASSWORD}" \
    /data/geometry/Colorado_County_Boundaries.geojson \
    -nln county -overwrite

if [ ${USE_HIGH_RES_TRACTS} = "1" ]; then
    # import tracts
    ogr2ogr -f "PostgreSQL" PG:"host=${POSTGRES_HOST} dbname=${POSTGRES_DATABASE} user=${POSTGRES_USER} password=${POSTGRES_PASSWORD}" \
        /data/geometry/Colorado_Census_Tract_Boundaries.geojson \
        -nln tract -overwrite
else
    # import simplified tracts
    ogr2ogr -f "PostgreSQL" PG:"host=${POSTGRES_HOST} dbname=${POSTGRES_DATABASE} user=${POSTGRES_USER} password=${POSTGRES_PASSWORD}" \
        /data/geometry/Colorado_Census_Tract_Boundaries_lessmid.geojson \
        -nln tract -overwrite
fi


# ========================================
# === catch up on migrations
# ========================================

# apply migrations at startup
alembic upgrade head


# ========================================
# === start the app
# ========================================

if [ "${IS_DEV}" = "1" ]; then
    uvicorn main:app --reload --host "${APP_HOST}" --port "${APP_PORT}"
else
    uvicorn main:app --host "${APP_HOST}" --port "${APP_PORT}"
fi

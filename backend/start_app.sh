#!/usr/bin/env bash

IS_DEV=${IS_DEV:-0}

APP_HOST="0.0.0.0"
APP_PORT="8000"

# if 1, uses high-resolution tracts, but at the cost of higher memory/data usage
USE_HIGH_RES_TRACTS=${USE_HIGH_RES_TRACTS:-0}


# ========================================
# === geometry import via ogr2ogr
# ========================================

# ensure the db is available before trying to import geometry
/opt/wait-for-it.sh ${POSTGRES_HOST}:${POSTGRES_PORT} --timeout=120

# import counties
ogr2ogr -f "PostgreSQL" PG:"host=${POSTGRES_HOST} dbname=${POSTGRES_DATABASE} user=${POSTGRES_USER} password=${POSTGRES_PASSWORD}" \
    /data/geometry/Colorado_County_Boundaries.geojson \
    -nln county -overwrite

# import CDPHE Colorado Health Statistics Regions
#  the "LAUNDER=NO" option is used to prevent the column names from being converted to lowercase
ogr2ogr -f "PostgreSQL" PG:"host=${POSTGRES_HOST} dbname=${POSTGRES_DATABASE} user=${POSTGRES_USER} password=${POSTGRES_PASSWORD}" \
    /data/geometry/CDPHE_Colorado_Health_Statistics_Regions.geojson \
    -lco LAUNDER=NO \
    -sql "SELECT hs_region, objectid, counties, 'Colorado' AS state FROM CDPHE_Colorado_Health_Statistics_Regions" \
    -nln healthregion -overwrite

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

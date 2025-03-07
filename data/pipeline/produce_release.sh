#!/usr/bin/env bash

# abort script on any error
set -euo pipefail

# identify where this script is located...
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
# ...and move one above it, to the /data folder
cd ${SCRIPT_DIR}/..

# --- configuration from the environment

# if NONINTERACTIVE=1, all prompts will be assumed to be 'no'
# this is to support running the pipeline in non-interactive contexts, such as
# in a CI/CD pipeline. you'll likely also want to set the following env vars:
# - FORCE_ACQUIRE_RELEASE=1
# - FORCE_DELETE_DB_BEFORE_IMPORT=1
# so that a new release is built and the current contents of the database are
# purged before importing data.
NONINTERACTIVE=${NONINTERACTIVE:-0}

# if FORCE_ACQUIRE_RELEASE=1, a new release will be built before importing data.
# if this value is 0 and NONINTERACTIVE=0, the user will be prompted to decide
# whether to acquire a new release.
ACQUIRE_RELEASE=${FORCE_ACQUIRE_RELEASE:-0}

# if FORCE_DELETE_DB_BEFORE_IMPORT=1, the database will be purged before
# importing data.
# if this value is 0 and NONINTERACTIVE=0, the user will be prompted to decide
# whether to delete the database before importing data.
DELETE_DB_BEFORE_IMPORT=${FORCE_DELETE_DB_BEFORE_IMPORT:-0}


# --- helper functions

# function to check if a container in the stack is healthy
# usage: wait_for_container_healthy <container_name> [poll_secs:1] [retries:60]
wait_for_container_healthy() {
    CONTAINER_NAME=$1
    CONTAINER_ID=$( docker compose ps -q ${CONTAINER_NAME} )

    # optional args: polling interval, number of retries
    POLL_SECS=${2:-1}
    RETRIES=${3:-60}
    RETRIES_LEFT=${RETRIES}

    if [ -z "${CONTAINER_ID}" ]; then
        echo "Container ${CONTAINER_NAME} not found in the stack"
        exit 1
    fi

    echo "Waiting for ${CONTAINER_NAME} to be healthy (retries: ${RETRIES})..."
    
    until docker inspect --format='{{json .State.Health.Status}}' ${CONTAINER_ID} | grep -q healthy; do
        echo "...still waiting for ${CONTAINER_NAME} to be healthy (retries left: ${RETRIES_LEFT})..."
        sleep ${POLL_SECS}

        # check if we've exceeded the number of retries
        if [ ${RETRIES_LEFT} -eq 0 ]; then
            echo "Container ${CONTAINER_NAME} did not become healthy in time"
            exit 1
        fi

        # decrement retries
        RETRIES_LEFT=$((RETRIES_LEFT-1))
    done
}


# -----------------------------------------------------------------------------
# --- stage 1. grab the requisite data for the release
# -----------------------------------------------------------------------------

# if we haven't been forced to create a release, ask the user if they'd like to
if [ "${ACQUIRE_RELEASE}" -eq 0 ] || [ "${NONINTERACTIVE}" -eq 1 ]; then
    read -p "Do you want to obtain a new release before importing data? (y/n) " -n 1 -r ; echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ACQUIRE_RELEASE=1
    fi
fi

# create the new release in the staging folder
if [ "${ACQUIRE_RELEASE}" -eq 1 ]; then
    # ensure the backend is up and running
    docker compose up -d backend && \
    wait_for_container_healthy backend

    # execute snakemake from /data/pipeline, which will write a new staging
    # release into /data/staging/<YYYY-MM-DD>
    docker compose exec -T backend /bin/bash -s <<-EOF
        cd /data/pipeline
        snakemake --cores all
EOF
fi


# -----------------------------------------------------------------------------
# --- stage 2. loading data and creating the dump
# -----------------------------------------------------------------------------

# get the latest versions by date of each file in the staging folder
LATEST_STAGING=$( ls --color=never ./staging/ | sort -rh | head -n 1 )

echo "* Populating the database with the latest data from the staging folder"
echo "  - Latest staging folder date: ${LATEST_STAGING}"

# if they haven't forced it already, ask the user if they want to purge the
# database before import
if [ "${DELETE_DB_BEFORE_IMPORT}" -eq 0 ] || [" ${NONINTERACTIVE}" -eq 1 ]; then
    read -p "Do you want to purge the database before importing data? (y/n) " -n 1 -r ; echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        DELETE_DB_BEFORE_IMPORT=1
    fi
fi

if [ "${DELETE_DB_BEFORE_IMPORT}" -eq 1 ]; then
    # bring down the stack
    docker compose down

    # identify the db data volume and delete it
    TARGET_VOLUME=$( docker volume ls | grep ecco_pgdata | tr -s ' ' | cut -d ' ' -f2 )
    echo "Purging the database volume (${TARGET_VOLUME})..."
    docker volume rm ${TARGET_VOLUME}
fi

# bring up only the db and backend, which are both needed for loading data
export SKIP_DB_LOAD=1 # ensure we don't load the most recent dump
docker compose up -d db backend

# wait for backend to be healthy by checking it via docker
wait_for_container_healthy backend

# run the commands to load the data into the database
# (this may report issues if the database is already populated, but all the ones
# i've seen so far are warnings that can be ignored. it's safest to start with
# an empty database if possible, in any case.)
docker compose exec -T backend /bin/bash -s <<EOF
cd /app
./commands/add_us_states.py 
./commands/import_cif_data.py --warn-on-missing-model True /data/staging/${LATEST_STAGING}/cif/stats/
./commands/import_scp_data.py /data/staging/${LATEST_STAGING}/scp/
./commands/import_cancer_disparities.py '/data/reference/coe-phsr/DT-COE.Cancer.Disparity.Indices.and.Treatment.Locations.by.County.xlsx'
./commands/import_radon.py '/data/reference/radon/TEEO_REF_CDPHE COEPHT Pre-Mitigation Radon Test Results_2023_EN.xlsx'
./commands/import_locations.py /data/reference/locations/locations.json /data/staging/${LATEST_STAGING}/locations/locations-data.json 
./commands/import_hpv.py /data/reference/cdphe-hpv/CO_Teen_Rates_anygender.xlsx /data/reference/cdphe-hpv/CO_Teen_Rates_female.xlsx /data/reference/cdphe-hpv/CO_Teen_Rates_male.xlsx
# ./commands/import_vaping_data.py '/data/reference/youth-vaping/sheets/2023 HKCS HS Regional Vapor Results.xlsx' '/data/reference/youth-vaping/sheets/2023 HKCS HS State Vapor Results.xlsx' 
./commands/import_ccc_state_stats.py /data/reference/ccc-team-data/ECCO_IncAverages.xlsx
EOF

# get into the database and make a new dump, which will be saved in /db-exports
# and loaded automatically by the database container on its next boot
docker compose exec -T db /bin/bash -s <<EOF
cd /db-exports
FORCE_OVERWRITE=1 ./make_db_export.sh
EOF

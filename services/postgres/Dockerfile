FROM postgis/postgis:15-3.4

# source Dockerfile for postgis/postgis:15-3.4:
# https://github.com/postgis/docker-postgis/blob/6c43b39522f2de801ee83f09f631af1f0fbc2aad/15-3.4/Dockerfile
# postgis/postgis:15-3.4 is based on postgres:15-bullseye; Dockerfile:
# https://github.com/docker-library/postgres/blob/8a0b96710d917d1c3b32a5fe5b66687ad83827da/15/bullseye/Dockerfile

# create a folder for scripts that get run after the db is initialized, whether
# or not the database already exists (as opposed to /docker-entrypoint-initdb.d,
# which only runs scripts if the database doesn't already exist)
RUN mkdir /docker-entrypoint-postinit.d

COPY ./healthcheck.sh /opt/healthcheck.sh

# override the entrypoint so it runs our post-init scripts after
# the regular entrypoint completes
COPY ./patched-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

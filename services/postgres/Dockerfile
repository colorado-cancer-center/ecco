FROM postgis/postgis:15-3.3

# create a folder for scripts that get run after the db is initialized, whether
# or not the database already exists (as opposed to /docker-entrypoint-initdb.d,
# which only runs scripts if the database doesn't already exist)
RUN mkdir /docker-entrypoint-postinit.d

COPY ./healthcheck.sh /opt/healthcheck.sh

# override the entrypoint so it runs our post-init scripts after
# the regular entrypoint completes
COPY ./patched-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

FROM python:3.10

# install a few system packages
RUN apt-get update && apt-get install -y gdal-bin jq

COPY ./requirements.txt /tmp/requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r /tmp/requirements.txt

# set our TZ to American/Denver, with the option
# to override it at build time via the arg 'TZ'
ARG TZ=America/Denver
ENV TZ=${TZ}

COPY ./start_app.sh /opt/start_app.sh

WORKDIR /app
COPY ./app/ /app

CMD ["/opt/start_app.sh"]

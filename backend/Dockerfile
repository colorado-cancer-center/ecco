FROM python:3.10

# install a few system packages
RUN apt-get update && apt-get install -y gdal-bin jq

COPY ./requirements.txt /tmp/requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r /tmp/requirements.txt

COPY ./start_app.sh /opt/start_app.sh

WORKDIR /app
COPY ./app/ /app

CMD ["/opt/start_app.sh"]

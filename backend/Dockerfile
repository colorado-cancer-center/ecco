FROM python:3.10

# install a few system packages
RUN apt-get update && apt-get install -y gdal-bin jq

# install node, since we need mapshaper, an npm package
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*
# install mapshaper
RUN npm install -g mapshaper

# install curl, certs, openssl
# patch in an intermediate cert that cancerinfocus is missing for some reason
RUN apt-get update && apt-get install -y --no-install-recommends \
   ca-certificates curl openssl && \
    curl -fsSL http://crt.sectigo.com/InCommonRSAServerCA2.crt \
      -o /tmp/InCommonRSAServerCA2.der && \
    openssl x509 -inform DER \
      -in /tmp/InCommonRSAServerCA2.der \
      -out /usr/local/share/ca-certificates/InCommonRSAServerCA2.crt && \
    update-ca-certificates && \
    rm -f /tmp/InCommonRSAServerCA2.der && \
    rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /tmp/requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r /tmp/requirements.txt

# set our TZ to American/Denver, with the option
# to override it at build time via the arg 'TZ'
ARG TZ=America/Denver
ENV TZ=${TZ}

COPY ./start_app.sh /opt/start_app.sh
COPY ./scripts/wait-for-it.sh /opt/wait-for-it.sh

WORKDIR /app
COPY ./app/ /app

CMD ["/opt/start_app.sh"]

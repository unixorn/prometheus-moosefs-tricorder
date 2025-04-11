FROM python:3.11-slim-bookworm AS build

ARG DEBIAN_FRONTEND=noninteractive

RUN set -eux; \
# installation
        apt-get update; \
        apt-get full-upgrade -y; \
        apt-get install -y --no-install-recommends \
                black \
                make \
                python3-poetry \
                python3-prometheus-client \
                ; \
        apt-get remove --purge --auto-remove -y; \
        rm -rf /var/lib/apt/lists/*

RUN mkdir /data

WORKDIR /data

COPY . .

RUN make wheel

FROM python:3.11-slim-bookworm

ARG application_version
LABEL maintainer="Joe Block <jpb@unixorn.net>"
LABEL version=${application_version}

RUN set -eux; \
# installation
        apt-get update; \
        apt-get full-upgrade -y; \
        apt-get install -y --no-install-recommends \
                moosefs-cli \
                python3-prometheus-client \
                ; \
        apt-get remove --purge --auto-remove -y; \
        rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/wheels
COPY --from=build /data/dist/*.whl /opt/wheels
RUN pip install /opt/wheels/*.whl

CMD [ "bash" ]

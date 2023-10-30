FROM python:3.11-slim-bookworm

ARG application_version
LABEL maintainer="Joe Block <jpb@unixorn.net>"
LABEL version=${application_version}

RUN apt-get update && \
    apt-get install -y ca-certificates moosefs-cli --no-install-recommends && \
    apt-get clean autoclean && \
    apt-get autoremove --yes && \
    rm -rf /var/lib/{apt,dpkg,cache,log}/ && \
    update-ca-certificates
RUN mkdir -p /opt/wheels && pip install --upgrade pip
COPY dist/*.whl /opt/wheels
RUN pip install --upgrade pip /opt/wheels/*.whl

CMD [bash]

# moosefs-tricorder

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
![Awesomebot](https://github.com/unixorn/prometheus-moosefs-tricorder/actions/workflows/awesomebot.yml/badge.svg)
![Mega-Linter](https://github.com/unixorn/prometheus-moosefs-tricorder/actions/workflows/mega-linter.yml/badge.svg)


Scrape a [moosefs](https://moosefs.com) master server with `mfscli` and export information to [prometheus](https://prometheus.io/) for further processing - graphing, alerting, etc.

I couldn't find documentation about the moosefs master's API. However, they do provide the `mfscli` command, and its output is parseable relatively easily.

I don't guarantee this will work with any version of the master other than 3.116, that's all I've tested it on.

## Installation

You have three options

- Install it via `pip install moosefs-tricorder` on a machine. You may run into irritations due to dependencies. You will also need to install `mfscli` - the exporter uses that to probe the master for statistics about the master, the chunkservers, and the moosefs filesystem.
- Use my docker image - `docker run -p 9877:9877 unixorn/moosefs-tricorder moosefs-prometheus-exporter --master YOUR_MOOSEFS_MASTER`. This image supports the linux/arm64, linux/amd64 and linux/arm/v7 architectures.
- Bake your own image with `make local`. You'll need to change `$HUB_USER` in the `Makefile`.

## Usage

If you install directly on your system, you can run `moosefs-prometheus-exporter`.

```Usage: moosefs-prometheus-exporter [-h] [-d] [-l {DEBUG,INFO,ERROR,WARNING,CRITICAL}] [--exporter-port EXPORTER_PORT (default 9877)]
                               [--master-port MASTER_PORT (default 9421)] [--moosefs-master MOOSEFS_MASTER] [--polling-interval POLLING_INTERVAL_IN_SECONDS (default 15)]
```

If you're running it in `docker`, you can either run `docker run -p 9877:9877 unixorn/moosefs-tricorder moosefs-prometheus-exporter --master YOUR_MOOSEFS_MASTER`, or use docker-compose.

```yaml
---
# example docker-compose.yaml
version: '3'

services:
  moosefs-tricorder:
    image: unixorn/moosefs-tricorder:latest
    container_name: moosefs-tricorder
    command: moosefs-prometheus-exporter --moosefs-master=mfsmaster.example.com
    ports:
      - 9877:9877
    restart: unless-stopped
    environment:
      - TZ=America/Denver
    volumes:
      - /etc/hostname:/etc/hostname:ro
      - /etc/localtime:/etc/localtime:ro
      - /etc/timezone:/etc/timezone:ro
```

## Contributors

<a href="https://github.com/unixorn/prometheus-moosefs-tricorder/graphs/contributors">
  <img src="https://contributors-img.web.app/image?repo=unixorn/prometheus-moosefs-tricorder" />
</a>

Made with [contributors-img](https://contributors-img.web.app).

# Copyright 2023 Joe Block <jpb@unixorn.net>
#
# pyright: ignore reportMissingImports

import logging
import time

from moosefs_tricorder.cli import parse_master_cli
from moosefs_tricorder.common import load_chunkserver_metrics, load_master_metrics
from prometheus_client import (  # pylint: disable=import-error
    GC_COLLECTOR,
    PLATFORM_COLLECTOR,
    PROCESS_COLLECTOR,
    start_http_server,
)

from prometheus_client.core import (  # pylint: disable=import-error
    REGISTRY,
    GaugeMetricFamily,
    InfoMetricFamily,
)
from prometheus_client.registry import Collector  # pylint: disable=import-error


class MooseCollector(Collector):
    def __init__(
        self,
        moosefs_master_port: int = 80,
        polling_interval: int = 5,
        moosefs_master: str = "localhost",
    ):
        self.moosefs_master = moosefs_master
        self.moosefs_master_port = moosefs_master_port
        self.polling_interval_seconds = polling_interval
        logging.debug(f"moosefs_master {moosefs_master}")
        logging.debug(f"moosefs_master_port {moosefs_master_port}")
        logging.debug(f"polling_interval {polling_interval}")

    def collect(self):
        """
        Collect moosefs statistics
        """
        moosefs_master_port = str(self.moosefs_master_port)
        master_data = load_master_metrics(moosefs_master=self.moosefs_master, moosefs_master_port=self.moosefs_master_port)
        # Master stats
        try:
            logging.info(f"Collecting master stats for {self.moosefs_master}:{self.moosefs_master_port}")
            m_all_cpu = GaugeMetricFamily(
                "moosefs_master_all_cpu",
                "moosefs master all cpu",
                labels=["moosefs_master", "moosefs_master_port"],
            )
            m_last_save_status = InfoMetricFamily(
                "moosefs_master_last_save_status",
                "moosefs master last save state",
                labels=["moosefs_master", "moosefs_master_port"],
            )
            m_ram_used = GaugeMetricFamily(
                "moosefs_master_ram_used",
                "moosefs master ram used",
                labels=["moosefs_master", "moosefs_master_port"],
            )
            m_sys_cpu = GaugeMetricFamily(
                "moosefs_master_sys_cpu",
                "moosefs master sys cpu",
                labels=["moosefs_master", "moosefs_master_port"],
            )
            m_user_cpu = GaugeMetricFamily(
                "moosefs_master_all_cpu",
                "moosefs master user cpu",
                labels=["moosefs_master", "moosefs_master_port"],
            )
            m_version = InfoMetricFamily(
                "moosefs_master_version",
                "moosefs master software version",
                labels=["moosefs_master", "moosefs_master_port"],
            )

            m_all_cpu.add_metric([self.moosefs_master, moosefs_master_port], master_data["all_cpu"])
            m_ram_used.add_metric([self.moosefs_master, moosefs_master_port], master_data["ram_used"])
            m_sys_cpu.add_metric([self.moosefs_master, moosefs_master_port], master_data["sys_cpu"])
            m_user_cpu.add_metric([self.moosefs_master, moosefs_master_port], master_data["user_cpu"])
            m_version.add_metric(
                [self.moosefs_master, moosefs_master_port], {"version": master_data["version"]}
            )
            m_last_save_status.add_metric(
                [self.moosefs_master, moosefs_master_port], {"version": master_data["last_save_status"]}
            )
            yield m_all_cpu
            yield m_ram_used
            yield m_sys_cpu
            yield m_user_cpu
            yield m_version

        except Exception as e:
            logging.error("Failed to create master metrics")
            logging.error(e)

        chunkserver_data = load_chunkserver_metrics(moosefs_master=self.moosefs_master, moosefs_master_port=self.moosefs_master_port)
        try:
            logging.debug("Parsing chunkserver data")
            cs_labels = InfoMetricFamily(
                "moosefs_chunkserver_labels",
                "Chunkserver labels",
                labels=["moosefs_master", "moosefs_master_port", "chunkserver", "port"],
            )
            cs_version = InfoMetricFamily(
                "moosefs_chunkserver_version",
                "Chunkserver version",
                labels=["moosefs_master", "moosefs_master_port", "chunkserver", "port"],
            )
            cs_maintenance = InfoMetricFamily(
                "moosefs_chunkserver_maintenance_status",
                "Chunkserver maintenance status",
                labels=["moosefs_master", "moosefs_master_port", "chunkserver", "port"],
            )
            cs_load = GaugeMetricFamily(
                "moosefs_chunkserver_load", "Chunkserver load",
                labels=["moosefs_master", "moosefs_master_port", "chunkserver", "port"]
            )
            cs_port = GaugeMetricFamily(
                "moosefs_chunkserver_port", "Chunkserver port",
                labels=["moosefs_master", "moosefs_master_port", "chunkserver", "port"]
            )
            cs_cs_id = GaugeMetricFamily(
                "moosefs_chunkserver_id", "Chunkserver ID",
                labels=["moosefs_master", "moosefs_master_port", "chunkserver", "port"]
            )
            cs_chunk_count = GaugeMetricFamily(
                "moosefs_chunkserver_chunk_count", "Chunk Count",
                labels=["moosefs_master", "moosefs_master_port", "chunkserver", "port"]
            )
            cs_disk_used = GaugeMetricFamily(
                "moosefs_chunkserver_disk_used", "Disk used",
                labels=["moosefs_master", "moosefs_master_port", "chunkserver", "port"]
            )
            cs_disk_total = GaugeMetricFamily(
                "moosefs_chunkserver_disk_total", "Disk total",
                labels=["moosefs_master", "moosefs_master_port", "chunkserver", "port"]
            )
            cs_disk_usage = GaugeMetricFamily(
                "moosefs_chunkserver_disk_usage", "Disk usage %",
                labels=["moosefs_master", "moosefs_master_port", "chunkserver", "port"]
            )

            cluster_chunk_count = GaugeMetricFamily(
                "moosefs_cluster_chunk_count",
                "Total chunk count in MooseFS cluster",
                labels=["cluster", "port"],
            )
            cluster_chunkserver_count = GaugeMetricFamily(
                "moosefs_cluster_chunkserver_count",
                "Chunkservers in MooseFS cluster",
                labels=["cluster", "port"],
            )
            cluster_disk_total = GaugeMetricFamily(
                "moosefs_cluster_disk_total",
                "Total disk available in MooseFS cluster",
                labels=["cluster", "port"],
            )
            cluster_disk_usage = GaugeMetricFamily(
                "moosefs_cluster_disk_usage",
                "Disk usage percentage in MooseFS cluster",
                labels=["cluster", "port"],
            )
            cluster_disk_used = GaugeMetricFamily(
                "moosefs_cluster_disk_used",
                "Total disk used in MooseFS cluster",
                labels=["cluster", "port"],
            )
            cluster_maintenance_count = GaugeMetricFamily(
                "moosefs_cluster_maintenance_count",
                "Chunkservers in maintenance mode in MooseFS cluster",
                labels=["cluster", "port"],
            )

            # Aggregate some statistics about the cluster
            mfs_chunk_count = 0
            mfs_chunkserver_count = 0
            mfs_disk_total = 0
            mfs_disk_used = 0
            mfs_maintenance_count = 0

            for cs in chunkserver_data.keys():
                mfs_chunkserver_count += 1
                port = str(chunkserver_data[cs]["port"])
                logging.debug(f"{cs}: {chunkserver_data[cs]}")
                # First, all the Info metrics
                if "labels" in chunkserver_data[cs]:
                    logging.debug(
                        f"{cs}: Adding label {chunkserver_data[cs]['labels']}"
                    )
                    cs_labels.add_metric(
                        [self.moosefs_master, moosefs_master_port, cs, port], value={"labels": chunkserver_data[cs]["labels"]}
                    )
                if "maintenance" in chunkserver_data[cs]:
                    logging.debug(
                        f"{cs}: Adding maintenance {chunkserver_data[cs]['maintenance']}"
                    )
                    cs_maintenance.add_metric(
                        [self.moosefs_master, moosefs_master_port, cs, port], value={"maintenance": chunkserver_data[cs]["maintenance"]}
                    )
                    if chunkserver_data[cs]["maintenance"] != "maintenance_off":
                        mfs_maintenance_count += 1
                if "version" in chunkserver_data[cs]:
                    logging.debug(
                        f"{cs}: Adding version {chunkserver_data[cs]['version']}"
                    )
                    cs_version.add_metric(
                        [self.moosefs_master, moosefs_master_port, cs, port], value={"version": chunkserver_data[cs]["version"]}
                    )
                # Now all the gauges
                if "chunk_count" in chunkserver_data[cs]:
                    logging.debug(
                        f"{cs}: Adding chunk_count {chunkserver_data[cs]['chunk_count']}"
                    )
                    mfs_chunk_count += int(chunkserver_data[cs]["chunk_count"])
                    cs_chunk_count.add_metric([self.moosefs_master, moosefs_master_port, cs, port], chunkserver_data[cs]["chunk_count"])
                if "cs_id" in chunkserver_data[cs]:
                    logging.debug(f"{cs}: Adding cs_id {chunkserver_data[cs]['cs_id']}")
                    cs_cs_id.add_metric([self.moosefs_master, moosefs_master_port, cs, port], chunkserver_data[cs]["cs_id"])
                if "disk_total" in chunkserver_data[cs]:
                    logging.debug(
                        f"{cs}: Adding disk_total {chunkserver_data[cs]['disk_total']}"
                    )
                    cs_disk_total.add_metric([self.moosefs_master, moosefs_master_port, cs, port], chunkserver_data[cs]["disk_total"])
                    mfs_disk_total += int(chunkserver_data[cs]["disk_total"])
                if "disk_usage" in chunkserver_data[cs]:
                    logging.debug(
                        f"{cs}: Adding disk_usage {chunkserver_data[cs]['disk_usage']}"
                    )
                    cs_disk_usage.add_metric([self.moosefs_master, moosefs_master_port, cs, port], chunkserver_data[cs]["disk_usage"])
                if "disk_used" in chunkserver_data[cs]:
                    logging.debug(
                        f"{cs}: Adding disk_used {chunkserver_data[cs]['disk_used']}"
                    )
                    cs_disk_used.add_metric([self.moosefs_master, moosefs_master_port, cs, port], chunkserver_data[cs]["disk_used"])
                    mfs_disk_used += int(chunkserver_data[cs]["disk_used"])
                if "load" in chunkserver_data[cs]:
                    logging.debug(f"{cs}: Adding load {chunkserver_data[cs]['load']}")
                    cs_load.add_metric([self.moosefs_master, moosefs_master_port, cs, port], chunkserver_data[cs]["load"])
                if "port" in chunkserver_data[cs]:
                    logging.debug(f"{cs}: Adding port {chunkserver_data[cs]['port']}")
                    cs_port.add_metric([self.moosefs_master, moosefs_master_port, cs, port], int(chunkserver_data[cs]["port"]))

            # Report aggregated cluster metrics
            mfs_disk_usage = float(mfs_disk_used / mfs_disk_total)

            logging.debug(f"mfs_chunk_count {mfs_chunk_count}")
            logging.debug(f"mfs_chunkserver_count {mfs_chunkserver_count}")
            logging.debug(f"mfs_disk_total {mfs_disk_total}")
            logging.debug(f"mfs_disk_usage {mfs_disk_usage}")
            logging.debug(f"mfs_disk_used {mfs_disk_used}")
            logging.debug(f"mfs_maintenance_count {mfs_maintenance_count}")

            cluster_chunk_count.add_metric([self.moosefs_master, moosefs_master_port], mfs_chunk_count)
            cluster_disk_total.add_metric([self.moosefs_master, moosefs_master_port], mfs_disk_total)
            cluster_disk_usage.add_metric([self.moosefs_master, moosefs_master_port], mfs_disk_usage)
            cluster_disk_used.add_metric([self.moosefs_master, moosefs_master_port], mfs_disk_used)
            cluster_maintenance_count.add_metric(
                [self.moosefs_master, moosefs_master_port], mfs_maintenance_count
            )
            cluster_chunkserver_count.add_metric(
                [self.moosefs_master, moosefs_master_port], mfs_chunkserver_count
            )

            # Cluster metrics
            yield cluster_chunk_count
            yield cluster_maintenance_count
            yield cluster_disk_used
            yield cluster_disk_total
            yield cluster_disk_usage
            yield cluster_chunkserver_count

            # If we do the yields inside the for loop, the output isn't
            # consolidated properly - it'll repeat lines for each chunk server
            # every time a new chunk server's stats are processed.
            yield cs_chunk_count
            yield cs_cs_id
            yield cs_disk_total
            yield cs_disk_usage
            yield cs_disk_used
            yield cs_labels
            yield cs_load
            yield cs_maintenance
            yield cs_port
            yield cs_version

        except Exception as e:
            logging.critical(f"fail: {e}")


def cluster_metrics_collector():
    cli = parse_master_cli()
    # Disable some default stuff not relevant to moosefs
    REGISTRY.unregister(GC_COLLECTOR)
    REGISTRY.unregister(PLATFORM_COLLECTOR)
    REGISTRY.unregister(PROCESS_COLLECTOR)

    logging.info("Loading mfsmaster scrape parameters...")
    logging.info(f"exporter_port: {cli.exporter_port}")
    logging.info(f"moosefs_master: {cli.moosefs_master}")
    logging.info(f"moosefs_master_port: {cli.master_port}")
    logging.info(f"polling_interval_seconds: {cli.polling_interval}")

    logging.info(f"Starting moosefs prometheus exporter on {cli.exporter_port}")
    start_http_server(cli.exporter_port)
    REGISTRY.register(
        MooseCollector(
            moosefs_master=cli.moosefs_master,
            moosefs_master_port=cli.master_port,
            polling_interval=cli.polling_interval,
        )
    )
    while True:
        time.sleep(cli.polling_interval)

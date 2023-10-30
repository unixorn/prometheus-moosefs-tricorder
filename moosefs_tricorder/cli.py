# Copyright 2023 Joe Block <jpb@unixorn.net>

import argparse
import logging


def parse_master_cli():
    """
    Parse the command line options for probing a moosefs master
    """
    parser = argparse.ArgumentParser(
        description="Scrape moosefs master for chunkserver stats"
    )
    parser.add_argument("-d", "--debug", help="Debug setting", action="store_true")
    parser.add_argument(
        "-l",
        "--log-level",
        type=str.upper,
        help="set log level",
        choices=["DEBUG", "INFO", "ERROR", "WARNING", "CRITICAL"],
        default="INFO",
    )
    parser.add_argument(
        "--exporter-port",
        help="Run exporter on this port for prometheus to probe",
        type=int,
        default=9877,
    )
    parser.add_argument(
        "--master-port", help="Port on moosefs master", type=int, default=9421
    )
    parser.add_argument(
        "--moosefs-master",
        help="DNS/IP of moosefs master",
        type=str,
        default="localhost",
    )
    parser.add_argument(
        "--polling-interval", help="Polling interval in seconds", type=int, default=15
    )
    cli = parser.parse_args()

    loglevel = getattr(logging, cli.log_level.upper(), None)
    logFormat = "[%(asctime)s][%(levelname)8s][%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
    logging.basicConfig(level=loglevel, format=logFormat)
    logging.info("Set log level to %s", cli.log_level.upper())
    return cli

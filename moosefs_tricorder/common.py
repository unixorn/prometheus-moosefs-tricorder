# Copyright 2023 Joe Block <jpb@unixorn.net>

import logging
import subprocess
import time
from operator import itemgetter


def run(command: str):
    """
    Run a command an return its output
    """
    logging.debug(f"Running {command}...")
    cmd = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (output, err) = cmd.communicate()

    # Wait for it to terminate
    cmd_status = cmd.wait()
    if cmd_status != 0:
        err_msg = f"{command} exited {cmd_status}. \noutput={output}\nerr={err}"
        logging.error(err_msg)
        raise Exception(err_msg)
    return (output, err)


def load_chunkserver_metrics(moosefs_master: str) -> dict:
    """
    Load chunkserver metrics
    """
    logging.info("Loading chunkserver metrics...")
    command = f"mfscli -H {moosefs_master} -SCS -s^"
    stderr, _ = run(command)
    output = stderr.decode().split("\n")
    logging.debug(f"output: {output}")
    data = {}
    for line in output:
        try:
            chunks = line.strip().split("^")
            (
                chunkserver,
                port,
                cs_id,
                labels,
                version,
                load,
                maintenance,
                chunk_count,
                disk_used,
                disk_total,
            ) = itemgetter(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)(chunks)
            data[chunkserver] = {}
            data[chunkserver]["port"] = int(port)
            data[chunkserver]["cs_id"] = int(cs_id)
            data[chunkserver]["labels"] = labels
            data[chunkserver]["version"] = version
            data[chunkserver]["load"] = int(load)
            data[chunkserver]["maintenance"] = maintenance
            data[chunkserver]["chunk_count"] = int(chunk_count)
            data[chunkserver]["disk_used"] = int(disk_used)
            data[chunkserver]["disk_total"] = int(disk_total)
            data[chunkserver]["disk_usage"] = int(disk_used) / int(disk_total)
            logging.debug(f"{chunkserver}: {data[chunkserver]}")
        except Exception as e:
            logging.error(f"Bad line: {line}")
            logging.error(f"chunks: {line.strip().split('^')}")
            logging.error(e)
    logging.debug(f"data: {data}")
    return data


def load_master_metrics(moosefs_master) -> dict:
    """
    Load master metrics
    """
    logging.info(f"Loading metrics for master node {moosefs_master}...")
    command = f"mfscli -H {moosefs_master} -SIM -s_"
    logging.debug(f"Running {command}")
    output, err = run(command)
    logging.debug(f"output: {output}")
    chunks = output.decode().strip().split("_")
    logging.debug(f"split: {chunks}")
    logging.debug(f"split: {len(chunks)}")
    logging.debug(f"err: {err}")
    (
        ip,
        version,
        state,
        local_time,
        metadata_version,
        metadata_delay,
        ram_used,
        raw_machine_stats,
        last_metadata_save,
        last_save_duration,
        last_save_status,
        exports_checksum,
    ) = itemgetter(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)(chunks)
    r_all, r_sys, r_user = itemgetter(0, 1, 2)(raw_machine_stats.split())
    all_cpu = r_all.split(":")[1].split("%")[0]
    sys_cpu = r_sys.split(":")[1].split("%")[0]
    user_cpu = r_user.split(":")[1].split("%")[0]

    metrics = {}
    metrics["all_cpu"] = float(all_cpu)
    metrics["exports_checksum"] = exports_checksum
    metrics["ip"] = ip
    metrics["last_metadata_save"] = last_metadata_save
    metrics["last_save_duration"] = float(last_save_duration)
    metrics["last_save_status"] = last_save_status
    metrics["local_time"] = time.strftime(
        "%Y-%m-%d %H:%M:%S", time.gmtime(float(local_time))
    )
    metrics["master_host"] = moosefs_master
    metrics["metadata_delay"] = metadata_delay
    metrics["metadata_version"] = metadata_version
    metrics["ram_used"] = int(ram_used)
    metrics["state"] = state
    metrics["sys_cpu"] = float(sys_cpu)
    metrics["user_cpu"] = float(user_cpu)
    metrics["version"] = version
    logging.debug(metrics)
    return metrics

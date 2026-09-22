#
# Title: collector.py
# Description: generate the json header for a power file
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#
import datetime
import logging
import os
import sys
import zoneinfo
from typing import Any

import yaml
from yaml.loader import SafeLoader

from helper.json_helper import JsonHelper
from power_file import PowerFile
from power_peaker import PowerPeaker

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("mastodon")


class Collector:
    def __init__(self, args: dict[str, Any]):
        self.crate_name = args["crateName"]
        self.fresh_dir = args["freshDir"]

        self.host_name = args["equipment"]["hostName"]
        self.host_type = args["equipment"]["hostType"]

        self.altitude = args["geoLoc"]["altitude"]
        self.latitude = args["geoLoc"]["latitude"]
        self.longitude = args["geoLoc"]["longitude"]
        self.site_name = args["geoLoc"]["siteName"]

        self.antenna = args["receiver"]["antenna"]
        self.receiver_id = args["receiver"]["receiverId"]
        self.receiver_task = args["receiver"]["task"]
        self.receiver_type = args["receiver"]["type"]

    @staticmethod
    def _mode_from_task(task: str) -> str:
        if task.endswith("bs1-pk1"):
            return "bigsearch01"
        if task.endswith("wx1-pk1"):
            return "noaa-wx01"

        return "unknown"

    def execute(self, base_file_name: str, start_time: int) -> None:
        logger.info("collector execute: %s %s", base_file_name, start_time)

        # convert from CSV to power_file_rows objects
        csv_file_name = f"/tmp/{base_file_name}.csv"
        if not os.path.exists(csv_file_name):
            logger.error("CSV file does not exist: %s", csv_file_name)
            return

        pf = PowerFile(csv_file_name)
        power_epoch_map = pf.parser()
        pp = PowerPeaker(power_epoch_map)

        mode = self._mode_from_task(self.receiver_task)
        peakers_list = pp.discover_peakers()

        dt_object_utc = datetime.datetime.fromtimestamp(
            start_time, tz=zoneinfo.ZoneInfo("UTC")
        )

        results = {
            "equipment": {
                "antenna": self.antenna,
                "receiverId": self.receiver_id,
                "receiverType": self.receiver_type,
                "hostName": self.host_name,
                "hostType": self.host_type,
            },
            "geoLoc": {
                "altitude": self.altitude,
                "latitude": self.latitude,
                "longitude": self.longitude,
                "siteName": self.site_name,
            },
            "job": {
                "mode": mode,
                "project": "mastodon-v1",
                "task": self.receiver_task,
            },
            "timeStamp": {
                "epochSeconds": start_time,
                "iso8601": dt_object_utc.isoformat(),
            },
            "crateName": self.crate_name,
            "fileName": f"{base_file_name}.json",
            "version": 1,
            "peakers": peakers_list,
        }

        outfile_json = f"{self.fresh_dir}/{base_file_name}.json"
        JsonHelper().json_file_writer(outfile_json, results)


#
# argv[1] = base filename
# argv[2] = start time
# argv[3] = optional configuration filename
#
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(
            "usage: python3 collector.py <base_name> <time_stamp> [configuration_file]"
        )
        sys.exit(1)

    base_name = sys.argv[1]
    start_time = int(sys.argv[2])
    file_name = sys.argv[3] if len(sys.argv) > 3 else "config.yaml"

    try:
        with open(file_name, "r", encoding="utf-8") as in_file:
            configuration = yaml.load(in_file, Loader=SafeLoader)
            collector = Collector(configuration)
            collector.execute(base_name, start_time)
    except FileNotFoundError:
        logger.error("configuration file not found: %s", file_name)
        sys.exit(1)
    except yaml.YAMLError as error:
        logger.error("YAML parse error: %s", error)
        sys.exit(1)
    except Exception as error:
        logger.error("collector execution failed: %s", error)
        sys.exit(1)

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***

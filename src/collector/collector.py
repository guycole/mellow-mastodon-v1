#
# Title: collector.py
# Description: generate the json header for a power file 
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#
import datetime
import json
import logging
import sys
import time
from tracemalloc import start
import uuid
import zoneinfo

from power_peaker import PowerPeaker
from power_file import PowerFile

import yaml
from yaml.loader import SafeLoader

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("mastodon")

class Collector:
    def __init__(self, args: dict[str, any]):
        self.crate_name = args["crateName"]
        self.fresh_dir = args["freshDir"]

        self.host_name = args['equipment']["hostName"]
        self.host_type = args['equipment']["hostType"]

        self.altitude = args["geoLoc"]["altitude"]
        self.latitude = args["geoLoc"]["latitude"]
        self.longitude = args["geoLoc"]["longitude"]
        self.site_name = args["geoLoc"]["siteName"]

        self.antenna = args["receiver"]["antenna"]
        self.receiver_id = args["receiver"]["receiverId"]
        self.receiver_task = args["receiver"]["task"]
        self.receiver_type = args["receiver"]["type"]

    def json_file_writer(self, file_name: str, json_data: dict[str, any]) -> None:
        try:
            with open(file_name, "w") as out_file:
                json.dump(json_data, out_file, indent=4)
        except Exception as error:
            print(error)

    def execute(self, base_file_name: str, start_time: int) -> None:
        logger.info(f"collector execute: {base_file_name} {start_time}")

        # convert from CSV to power_file_rows objects
        csv_file_name = f"/tmp/{base_file_name}.csv"
        pf = PowerFile(csv_file_name)
        power_epoch_map = pf.parser()

        pp = PowerPeaker(power_epoch_map)
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
                "siteName": self.site_name
            },
            "job": {
                "mode": "bigsearch01",
                "project": "mastodon-v1",
                "task": "mastodon-v1-bs1",
            },
            "timeStamp": {
                "epochSeconds": start_time,
                "iso8601": dt_object_utc.isoformat()
            },
            "crateName": self.crate_name,
            "fileName": f"{base_file_name}.json",
            "version": 1,
            "peakers": peakers_list,
        }

        outfile_json = f"{self.fresh_dir}/{base_file_name}.json"
        self.json_file_writer(outfile_json, results)

#
# argv[1] = configuration filename
#
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: python3 collector.py <base_name> <time_stamp>")
        sys.exit(1)

    file_name = "config.yaml"
    base_name = sys.argv[1]
    start_time = int(sys.argv[2])
   
    with open(file_name, "r") as in_file:
        try:
            configuration = yaml.load(in_file, Loader=SafeLoader)
            collector = Collector(configuration)
            collector.execute(base_name, start_time)
        except yaml.YAMLError as error:
            print(error)

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***

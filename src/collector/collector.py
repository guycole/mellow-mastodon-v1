#
# Title: collector.py
# Description: generate the json header for a power file 
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#
import datetime
import json
import sys
import time
import uuid
import zoneinfo

import yaml
from yaml.loader import SafeLoader

class Collector:

    def __init__(self, args: dict[str, any]):
        self.crate_name = args["crateName"]
        self.fresh_dir = args["freshDir"]

        self.host_name = args['equipment']["hostName"]
        self.host_type = args['equipment']["type"]

        self.altitude = args["geoLoc"]["altitude"]
        self.latitude = args["geoLoc"]["latitude"]
        self.longitude = args["geoLoc"]["longitude"]
        self.site_name = args["geoLoc"]["siteName"]

        self.antenna = args["receiver"]["antenna"]
        self.receiver_id = args["receiver"]["receiver_id"]
        self.receiver_type = args["receiver"]["type"]

    def json_file_writer(self, file_name: str, json_data: dict[str, any]) -> None:
        try:
            with open(file_name, "w") as out_file:
                json.dump(json_data, out_file, indent=4)
        except Exception as error:
            print(error)

    def execute(self, base_file_name: str) -> None:
        print(f"collector execute")
        print(f"base filename: {base_file_name}")

        outfile_json = f"{self.fresh_dir}/{base_file_name}.json"

        epoch_seconds = int(time.time())
        dt_object_utc = datetime.datetime.fromtimestamp(
            epoch_seconds, tz=zoneinfo.ZoneInfo("UTC")
        )

        results = {
            "equipment": {
                "antenna": self.antenna,  
                "receiver_id": self.receiver_id,
                "receiver_type": self.receiver_type,
                "platform": self.host_type,
                "hostName": self.host_name  
            },
            "geoLoc": {
                "altitude": self.altitude,
                "latitude": self.latitude,
                "longitude": self.longitude,
                "siteName": self.site_name
            },
            "timeStamp": {
                "epochSeconds": epoch_seconds,
                "iso8601": dt_object_utc.isoformat()
            },
            "crate": self.crate_name,
            "fileName": f"{base_file_name}.json",
            "mode": "big-search01",
            "project": "mastodon-v1",
            "version": 1
        }

        self.json_file_writer(outfile_json, results)

#
# argv[1] = configuration filename
#
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: python3 collector.py <configuration filename> <uuid>")
        sys.exit(1)

    file_name = sys.argv[1]
    base_name = sys.argv[2]
   
    with open(file_name, "r") as in_file:
        try:
            configuration = yaml.load(in_file, Loader=SafeLoader)
            collector = Collector(configuration)
            collector.execute(base_name)
        except yaml.YAMLError as error:
            print(error)

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***

#
# Title: collector.py
# Description: generate the json header for a power file
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#

import datetime
import logging
import os
import pydantic
import sys
import time
import zoneinfo
from typing import Any

import yaml
from yaml.loader import SafeLoader

from abc import ABC, abstractmethod

from helper.json_helper import JsonHelper
from power_file import PowerFile
from power_peaker import PowerPeaker

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("mastodon")


class Equipment(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(populate_by_name=True)

    host_name: str = pydantic.Field(alias="hostName")
    host_type: str = pydantic.Field(alias="hostType")


class GeoLoc(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(populate_by_name=True)

    altitude: float
    latitude: float
    longitude: float
    site_name: str = pydantic.Field(alias="siteName")


class Job(pydantic.BaseModel):
    mode: str
    project: str
    task: str


class Peaker(pydantic.BaseModel):
    frequency_hz: int
    measured_dbm: float
    background_dbm: float


class Receiver(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(populate_by_name=True)

    antenna: str
    receiver_id: int = pydantic.Field(alias="receiverId")
    task: str
    type: str


class TimeStamp(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(populate_by_name=True)

    epoch_seconds: int = pydantic.Field(
        default_factory=lambda: int(time.time()), alias="epochSeconds"
    )

    iso8601: str = ""

    @pydantic.model_validator(mode="after")
    def sync_iso8601_from_epoch(self) -> "TimeStamp":
        self.iso8601 = datetime.datetime.fromtimestamp(
            self.epoch_seconds, tz=zoneinfo.ZoneInfo("UTC")
        ).isoformat()
        return self


class MastodonModel(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(populate_by_name=True)

    crate_name: str = pydantic.Field(alias="crateName")
    file_name: str = pydantic.Field(alias="fileName")
    version: int = 2
    equipment: Equipment
    geo_loc: GeoLoc = pydantic.Field(alias="geoLoc")
    job: Job
    time_stamp: TimeStamp = pydantic.Field(alias="timeStamp")
    peakers: list[Peaker]

class Collector(ABC):
    @abstractmethod
    def get_peakers(self, base_file_name: str) -> list[Peaker]:
        pass

    @abstractmethod
    def execute(self, base_file_name: str, start_time: int) -> int:
        pass
  
class MastodonCollector(Collector):
    def __init__(self, args: dict[str, Any]):
        self.crate_name = args["crateName"]
        self.fresh_dir = args["freshDir"]

        self.equipment = Equipment(**args["equipment"])
        self.geo_loc = GeoLoc(**args["geoLoc"])
        self.receiver = Receiver(**args["receiver"])
        self.time_stamp = TimeStamp()

        task = args["receiver"]["task"]

        mode = "unknown"
        if task.endswith("bs1-pk1"):
            mode = "bigsearch01"
        if task.endswith("wx1-pk1"):
            mode = "noaa-wx01"

        project = task
        self.job = Job(mode=mode, project=project, task=task)

    def get_peakers(self, base_file_name: str) -> list[Peaker]:
        csv_file_name = f"/tmp/{base_file_name}.csv"
        if not os.path.exists(csv_file_name):
            logger.error("CSV file does not exist: %s", csv_file_name)
            return []

        power_file = PowerFile(csv_file_name)
        power_epoch_map = power_file.parser()
        power_peaker = PowerPeaker(power_epoch_map)
        raw_peakers = power_peaker.discover_peakers()

        return [
            Peaker(
                frequency_hz=int(peaker[0]),
                measured_dbm=float(peaker[1]),
                background_dbm=float(peaker[2]),
            )
            for peaker in raw_peakers
        ]

    def execute(self, base_file_name: str, start_time: int) -> int:
        logger.info("collector execute: %s %s", base_file_name, start_time)

        peakers_list = self.get_peakers(base_file_name)
        if not peakers_list:
            return 1
 
        mastodon_model = MastodonModel(
            crateName=self.crate_name,
            fileName=f"{base_file_name}.json",
            equipment=self.equipment,
            geoLoc=self.geo_loc,
            job=self.job,
            timeStamp=TimeStamp(epochSeconds=start_time),
            peakers=peakers_list,
        )

        outfile_json = f"{self.fresh_dir}/{base_file_name}.json"
        with open(outfile_json, "w", encoding="utf-8") as out_file:
            out_file.write(mastodon_model.model_dump_json(indent=4, by_alias=True))

        return 0


# Backward-compatible import surface for existing callers/tests.
Collector = MastodonCollector

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
            collector = MastodonCollector(configuration)
            sys.exit(collector.execute(base_name, start_time))
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

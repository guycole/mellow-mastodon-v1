#
# Title: mastodon_file.py
# Description:
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#

import csv
import datetime
import json
import sys
import time
import uuid

from postgres import PostGres

from sql_table import Equipment, Site


class MastodonFile:
    def __init__(self, postgres: PostGres):
        self.postgres = postgres

    def database_write(
        self, meta_map: dict[str, any], peaker_list: list[tuple]
    ) -> bool:
        dt = datetime.datetime.fromtimestamp(meta_map["time_stamp_epoch"])

        meta_map["population"] = len(peaker_list)

        load_log = self.postgres.load_log_insert(meta_map)
        if load_log is None:
            print("load log failure")
            return False

        for element in peaker_list:
            obs_args = {
                "freq_hz": element[0],
                "load_log_id": load_log.id,
                "rolling_mean": element[2],
                "signal_dbm": element[1],
            }

            obs = self.postgres.observation_insert(obs_args)
            if obs is None:
                print("obs insert failure")
                return False

            pop = self.postgres.population_select_by_frequency_site_id(
                element[0], meta_map["site_id"]
            )
            if len(pop) < 1:
                pop_args = {
                    "case_uuid": "10514480-5caf-4a41-98f2-a57eb24c2f9b",
                    "freq_hz": element[0],
                    "note": "noNote",
                    "obs_first": dt,
                    "obs_last": dt,
                    "population": 1,
                    "site_id": meta_map["site_id"],
                }

                pop = self.postgres.population_insert(pop_args)
                if pop is None:
                    print("population insert failure")
                    return False
            else:
                candidate = pop[0]

                candidate.population += 1

                if candidate.obs_first > dt:
                    candidate.obs_first = dt
                elif candidate.obs_last < dt:
                    candidate.obs_last = dt

                pop = self.postgres.population_update(candidate)

        return True

    def json_reader(self, file_name: str) -> dict[str, any]:
        results = {}

        try:
            with open(file_name, "r") as in_file:
                results = json.load(in_file)
        except Exception as error:
            print(error)

        return results

    def meta(self, file_name: str, raw_json: dict[str, any]) -> dict[str, any]:
        # {'antenna': 'discone1', 'file_type': 'mastodon-v1', 'project': 'big-search01', 'receiver': 'rtl-sdr-14', 'site': 'anderson1', 'time_stamp_epoch': 1756751283}

        equipment = self.postgres.equipment_select(
            raw_json["antenna"], raw_json["project"], raw_json["receiver"]
        )
        equipment_id = equipment.id

        site = self.postgres.site_select_by_name(raw_json["site"])

        if "schemaVersion" not in raw_json:
            raw_json["schemaVersion"] = 0
            raw_json["timeStampEpoch"] = raw_json["time_stamp_epoch"]

        return {
            "equipment_id": equipment_id,
            "file_name": file_name,
            "project": raw_json["project"],
            "schema_version": raw_json["schemaVersion"],
            "site_id": site.id,
            "time_stamp_epoch": raw_json["timeStampEpoch"],
        }

    def peakers(self, raw_json: dict[str, any]) -> list[tuple]:
        results = []

        for element in raw_json:
            if len(element) == 2:
                results.append((element[0], element[1], 0)) # pad missing average
            else:
                results.append((element[0], element[1], element[2]))

        return results

    def processor(self, file_name: str) -> bool:
        raw_json = self.json_reader(file_name)
        if len(raw_json) < 1:
            print(f"skipping empty file {file_name}")
            return False

        meta_map = self.meta(file_name, raw_json["meta"])
        if len(meta_map) < 1:
            print(f"skipping bad meta {file_name}")
            return False

        peaker_list = self.peakers(raw_json["peakers"])
        if len(peaker_list) < 1:
            print(f"skipping zero observations {file_name}")
            return False

        selected = self.postgres.load_log_select_by_file_name(file_name)
        if selected is not None:
            print(f"skipping known file {file_name}")
            return False

        return self.database_write(meta_map, peaker_list)


# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***

#
# Title: json_helper.py
# Description:
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#

import datetime
import json
import os
import time

from jsonschema import validate

from sql_table import Equipment, LoadLog, Observation, Population, Site

schema = {
    "type": "object",
    "properties": {
        "project": {"type": "string"},
        "schemaVersion": {"type": "number"},
        "caseId": {"type": "string", "format": "uuid"},
        "freqBins": {"type": "array", "items": {"type": "number"}},
        "freqHz": {"type": "number"},
        "modulation": {"type": "string"},
        "name": {"type": "string"},
        "note": {"type": "string"},
        "obsFirstEpochTime": {"type": "number"},
        "obsLastEpochTime": {"type": "number"},
        "obsSite": {"type": "string"},
        "samples": {
            "type": "array",
            "items": {"type": "string", "format": "uuid"},
        },
    },
    "required": [
        "project",
        "schemaVersion",
        "caseId",
        "freqBins",
        "freqHz",
        "modulation",
        "name",
        "note",
        "obsFirstEpochTime",
        "obsLastEpochTime",
        "obsSite",
    ],
    "additionalProperties": False,
}


class JsonHelper:
    def __init__(self, case_dir: str):
        self.case_dir = case_dir

    def full_file_name(self, case_uuid: str) -> str:
        return f"{self.case_dir}/{case_uuid}.json"

    def fresh_population_to_json(
        self, pop: Population, project: str, site: Site
    ) -> dict[str, any]:
        """convert a fresh case file"""

        return {
            "project": project,
            "schemaVersion": 1,
            "caseId": pop.case_uuid,
            "freqBins": [pop.freq_hz],
            "freqHz": pop.freq_hz,
            "modulation": "unknown",
            "name": "unknown",
            "note": pop.note,
            "obsFirstEpochTime": int(pop.obs_first.timestamp()),
            "obsLastEpochTime": int(pop.obs_last.timestamp()),
            "obsSite": site.name,
            "samples": [],
        }

    def update_population_json(self, args: dict[str, any], pop: Population) -> None:
        pass

    def json_reader(self, case_id: str) -> dict[str, any]:
        file_name = self.full_file_name(case_id)
        print(f"read {file_name}")

        if os.path.isfile(file_name) is False:
            print(f"missing {file_name}")
            return {}

        results = {}

        try:
            with open(file_name, "r") as in_file:
                results = json.load(in_file)
                validate(instance=results, schema=schema)
        except Exception as error:
            print(error)
            return {}

        return results

    def json_writer(self, payload: dict[str, any]) -> None:
        file_name = self.full_file_name(payload["caseId"])

        try:
            with open(file_name, "w") as out_file:
                json.dump(payload, out_file, indent=4)
        except Exception as error:
            print(error)


# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***

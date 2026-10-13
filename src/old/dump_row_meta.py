#
# Title: dump_row_meta.py
# Description: dump row metadata from mastodon csv
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#

import csv
import datetime
import json
import os
import sys
import time

from unittest import result
import uuid

import yaml
from yaml.loader import SafeLoader

from power_file_helper import MastodonHelper
from mastodon_row import MastodonRow


class CsvJson:
    def __init__(self, configuration: dict[str, str]):
        #        self.archive_dir = configuration["archiveDir"]
        self.cooked_dir = configuration["cookedDir"]
        #        self.failure_dir = configuration["failureDir"]
        self.fresh_dir = configuration["freshDir"]
        self.processed_dir = configuration["processedDir"]
        self.test_dir = configuration["testDir"]

        self.peaker_only = configuration["peakerOnly"]
        self.test_mode = configuration["testModeEnable"]

    def file_name(self, payload: MastodonRow) -> str:
        bin_seconds = payload.json_bag["meta"]["time_stamp_epoch"]
        freq_low_hz = payload.json_bag["meta"]["freq_low_hz"]
        project = payload.json_bag["project"]
        site = payload.json_bag["site"]

        return f"{self.cooked_dir}/{bin_seconds}-{freq_low_hz}-{project}.{site}"

    def json_reader(self, file_name: str) -> dict[str, any]:
        results = {}

        try:
            with open(file_name, "r") as in_file:
                results = json.load(in_file)
        except Exception as error:
            print(error)

        return results

    def json_writer(self, payload: MastodonRow, peaker_only_flag: bool) -> None:
        file_name = f"{self.file_name(payload)}.json"

        del payload.json_bag["meta"][
            "time_stamp_dt"
        ]  # datetime is not json serializable

        if peaker_only_flag:
            peakers_only = []

            for sample in payload.json_bag["samples"]:
                if sample[3] is True:
                    peakers_only.append(sample)

            payload.json_bag["samples"] = peakers_only

        try:
            with open(file_name, "w") as out_file:
                json.dump(payload.json_bag, out_file, indent=4)
        except Exception as error:
            print(error)

    # plot for [col=2:3] '1754987499-123569850-big-search.anderson1.gp' using 1:col
    def gnuplot_writer(self, payload: MastodonRow) -> None:
        file_name = f"{self.file_name(payload)}.gp"

        try:
            with open(file_name, "w") as out_file:
                for current in payload.json_bag["samples"]:
                    out_file.write(f"{current[0]}\t{current[1]}\t{current[2]}\n")
        except Exception as error:
            print(error)

    def csv_file_converter(self, file_name: str, personality: dict[str, any]) -> bool:
        helper = MastodonHelper()
        buffer = helper.csv_file_reader(file_name)

        for current in buffer:
            try:
                row = MastodonRow(file_name, personality)
                row.row_meta(current[0:6])
                row.row_samples(current)

                if self.peaker_only:
                    pass
                else:
                    self.gnuplot_writer(row)

                self.json_writer(row, self.peaker_only)
            except Exception as error:
                print(error)
                return False

        return True

    def execute(self) -> None:
        if self.test_mode:
            print(f"test dir:{self.test_dir}")
            os.chdir(self.test_dir)
        else:
            print(f"fresh dir:{self.fresh_dir}")
            os.chdir(self.fresh_dir)

        targets = os.listdir(".")
        print(f"{len(targets)} files noted")

        for target in targets:
            print(f"processing {target}")

            if os.path.isfile(target) is False:
                print(f"skipping {target}")
                continue

            personality = {}
            if target.endswith(".json"):
                personality = self.json_reader(target)
            else:
                print(f"skipping non-json file: {target}")
                continue

            if len(personality) < 1:
                print(f"skipping empty personality: {target}")
                continue

            power_name = target.split(".")[0]
            ret_flag = self.csv_file_converter(power_name, personality)

            if self.test_mode:
                print(f"skipping file move")
            else:
                os.unlink(target)
                os.unlink(power_name)


#                os.rename(target, self.processed_dir + "/" + target)
#                os.rename(power_name, self.processed_dir + "/" + power_name)


class MastodonDiagnostic:
    def execute(self, file_name: str) -> None:
        print(f"processing {file_name}")

        helper = MastodonHelper()
        buffer = helper.csv_file_reader(file_name)

        personality = {
            "antenna": "antenna",
            "host": "host",
            "project": "project",
            "receiver": "receiver",
            "site": "site",
        }

        for current in buffer:
            row = MastodonRow(file_name, personality)
            row.row_meta(current[0:6])
            print(row.json_bag["meta"])


# /var/mellow/mastodon/diagnostic

print("start dump_row_meta")  #

#
# argv[1] = csv filename
#
if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
        md = MastodonDiagnostic()
        md.execute(file_name)
    else:
        print("need filename")
        exit(1)

print("stop dump_row_meta")

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***

#
# Title: json_peaker.py
# Description: read a mastodon json file and discover active emitters
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#

import csv
import datetime
import json
import os
import sys
import time
import uuid

import yaml
from yaml.loader import SafeLoader


class JsonPeaker:
    def __init__(self, configuration: dict[str, str]):
        self.cooked_dir = configuration["cookedDir"]

    def json_reader(self, file_name: str) -> dict[str, any]:
        results = {}

        try:
            with open(file_name, "r") as in_file:
                results = json.load(in_file)
        except Exception as error:
            print(error)

        return results

    def json_writer(self, file_name, payload: dict[str, any]) -> None:
        try:
            with open(file_name, "w") as out_file:
                json.dump(payload, out_file, indent=4)
        except Exception as error:
            print(error)

    def frequency_bin_converter(self, full_name: str) -> list[tuple[float, float]]:
        buffer = self.json_reader(full_name)

        avg_sample = 0
        min_sample = 0
        max_sample = -100
        total_samples = 0

        frequency_bins = []
        current_frequency = buffer["meta"]["freq_low"]
        for sample in buffer["meta"]["bin_samples"]:
            frequency_bins.append((current_frequency, sample))
            current_frequency += buffer["meta"]["freq_step"]

            total_samples += sample

            if sample < min_sample:
                min_sample = sample

            if max_sample < sample:
                max_sample = sample

        avg_sample = total_samples / len(buffer["meta"]["bin_samples"])

        print(f"average:{avg_sample} min:{min_sample} max:{max_sample}")

        return buffer

    def execute(self, infile: str) -> None:
        full_name = os.path.join(self.cooked_dir, infile)

        if os.path.isfile(full_name) is True:
            frequency_bins = self.frequency_bin_converter(full_name)
        else:
            print(f"skipping {full_name}")


print("start json_peaker")

#
# argv[1] = configuration filename
#
if __name__ == "__main__":
    if len(sys.argv) > 1:
        config_name = sys.argv[1]
    else:
        config_name = "config.yaml"

    with open(config_name, "r", encoding="utf-8") as in_file:
        try:
            configuration = yaml.load(in_file, Loader=SafeLoader)
        except yaml.YAMLError as error:
            print(error)

    # samples
    candidate = "1752539766-123569850-big-search.anderson1"
    # candidate = "1752539766-462058275-big-search.anderson1"

    jp = JsonPeaker(configuration)
    jp.execute(candidate)

print("stop json_peaker")

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***

#
# Title: power_file.py
# Description: process a rtl_power CSV file
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#
import json

from power_file_epoch import PowerFileEpoch
from power_file_helper import PowerFileHelper
from power_file_row import PowerFileRow


class PowerFile:
    def __init__(self, file_name: str):
        self.file_name = file_name

#    def __str__(self):
#        return f"PowerFile: {self.pf_meta_map['source_file']}"

    def json_writer(
        self,
        epoch_time: int,
        archive_dir: str,
        peakers_list: list[tuple[int, float, float]],
    ) -> None:
        self.meta_map["epoch_time"] = epoch_time

        file_name = f"{archive_dir}/{self.meta_map['project']}-{self.meta_map['epoch_time']}-{self.meta_map['site']}.json"

        self.json_meta_map = {
            "antenna": self.meta_map["antenna"],
            "peakerAlgorithm": self.meta_map["peaker_algorithm"],
            "peakerThreshold": self.meta_map["peaker_threshold"],
            "project": self.meta_map["project"],
            "receiver": self.meta_map["receiver"],
            "site": self.meta_map["site"],
            "schemaVersion": 1,
            "timeStampEpoch": epoch_time,
        }

        payload = {"meta": self.json_meta_map, "peakers": peakers_list}

        try:
            with open(file_name, "w") as out_file:
                json.dump(payload, out_file, indent=4)
        except Exception as error:
            print(error)

    def parser(self) -> dict[int, PowerFileEpoch]:
        """read csv file and convert each row"""

        # read all rows of csv file
        helper = PowerFileHelper()
        raw_buffer = helper.csv_file_reader(self.file_name)

        # convert each csv row into PowerFileRow object, store in power_epoch_map
        power_epoch_map = {}
        for raw_row in raw_buffer:
            try: 
                pfr = PowerFileRow(raw_row)
            except Exception as error:
                print(error)
                continue

            pfr.convert_samples()

            if pfr.validate_frequencies() is False:
                raise Exception("frequency validation failed")

            epoch_key = pfr.pfr_meta_map["time_stamp_epoch"]
            if epoch_key not in power_epoch_map:
                power_epoch_map[epoch_key] = PowerFileEpoch(epoch_key)

            power_epoch_map[epoch_key].add_sample(pfr)

        return power_epoch_map

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***

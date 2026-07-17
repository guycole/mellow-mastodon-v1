#
# Title: power_file_row.py
# Description: power file row domain class
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#
import datetime
import json
import statistics


class PowerFileRow:
    def __init__(self, raw_row: list[str]):
        # ['2025-05-16', ' 04:16:20', ' 966482608', ' 969275710', ' 2727.64']
        # "\tdate, time, Hz low, Hz high, Hz step, samples, dbm, dbm, ...

        if len(raw_row) < 6:
            raise Exception("bad row len")

        self.raw_row = raw_row
        self.samples_list = []
        self.spectrum_list = []
        self.statistics_map = {}

        row_date = raw_row[0].split("-")
        yy = int(row_date[0])
        mm = int(row_date[1])
        dd = int(row_date[2])

        row_time = raw_row[1].split(":")
        hour = int(row_time[0])
        minute = int(row_time[1])
        second = int(row_time[2])

        dt = datetime.datetime(yy, mm, dd, hour, minute, second)

        self.pfr_meta_map = {
            "freq_low_hz": int(raw_row[2]),
            "freq_high_hz": int(raw_row[3]),
            "freq_step_hz": float(raw_row[4]),
            "sample_quantity": int(raw_row[5]),
            "time_stamp_dt": dt,
            "time_stamp_epoch": int(dt.timestamp()),
            "time_stamp_iso8601": dt.isoformat(),
        }

    def __str__(self):
        return f"{self.pfr_meta_map['time_stamp_epoch']} {self.pfr_meta_map['freq_low_hz']} {self.pfr_meta_map['freq_high_hz']} {self.pfr_meta_map['freq_step_hz']}"

    def convert_samples(self):
        # convert from string to float
        # produces self.samples_list = [(dbm, frequency), ...]

        avg_sample = 0
        min_sample = 0
        max_sample = -100
        total_samples = 0

        current_frequency = self.pfr_meta_map["freq_low_hz"]
        step_frequency = self.pfr_meta_map["freq_step_hz"]

        for ndx in range(6, len(self.raw_row)):  # start at 6 to skip row metadata
            current_value = float(self.raw_row[ndx])
            self.samples_list.append((int(current_frequency), current_value))
            current_frequency += step_frequency


    def validate_frequencies(self) -> bool:
        """ensure the promised frequency range matches calculated range"""

        actual_low = self.samples_list[0][0]
        actual_high = self.samples_list[-1][0]

        predicted_low = self.pfr_meta_map["freq_low_hz"]
        predicted_high = self.pfr_meta_map["freq_high_hz"]

        if actual_low != predicted_low or actual_high != predicted_high:
            print(f"actual low: {actual_low} predicted low: {predicted_low}")
            print(f"actual high: {actual_high} predicted high: {predicted_high}")
            return False
        else:
            # print("passed")
            return True

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***
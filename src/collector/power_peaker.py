#
# Title: power_peaker.py
# Description: discover signal peakers
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#

import statistics
from typing import Any


class PowerPeaker:
    HALF_WINDOW_SIZE = 33
    GUARD_WINDOW_SIZE = 4
    SIGMA_MULTIPLIER = 5.0
    MINIMUM_DELTA_DB = 6.0
    MINIMUM_SIGMA_DB = 0.5

    def __init__(self, power_epoch_map: dict[int, Any]):
        self.power_epoch_map = power_epoch_map

    def _bin_peakers(self, samples_list: list[tuple[int, float]]) -> list[tuple[int, float, float]]:
        if len(samples_list) < 1:
            return []

        float_list = [row[1] for row in samples_list]
        row_baseline = statistics.median(float_list)
        result = []

        for ndx, sample in enumerate(samples_list):
            left_start = max(0, ndx - self.HALF_WINDOW_SIZE)
            left_stop = max(left_start, ndx - self.GUARD_WINDOW_SIZE)
            right_start = min(len(float_list), ndx + self.GUARD_WINDOW_SIZE + 1)
            right_stop = min(len(float_list), ndx + self.HALF_WINDOW_SIZE + 1)

            training_bins = float_list[left_start:left_stop]
            training_bins.extend(float_list[right_start:right_stop])
            if len(training_bins) < 4:
                training_bins = [value for sample_ndx, value in enumerate(float_list) if sample_ndx != ndx]

            local_baseline = row_baseline
            if len(training_bins) > 0:
                local_baseline = statistics.median(training_bins)

            deviations = [abs(value - local_baseline) for value in training_bins]
            local_mad = 0.0
            if len(deviations) > 0:
                local_mad = statistics.median(deviations)

            local_sigma = max(1.4826 * local_mad, self.MINIMUM_SIGMA_DB)
            detection_threshold = local_baseline + max(
                self.MINIMUM_DELTA_DB, self.SIGMA_MULTIPLIER * local_sigma
            )

            sample_frequency = sample[0]
            sample_value = sample[1]
            if sample_value > detection_threshold:
                result.append((sample_frequency, sample_value, local_baseline))

        return result

    def discover_peakers(self) -> list[tuple[int, float, float]]:
        discovered_map = {}

        sorted_epochs = sorted(self.power_epoch_map.keys())
        for epoch_key in sorted_epochs:
            epoch = self.power_epoch_map[epoch_key]

            sorted_rows = sorted(epoch.pfe_pfr_map.keys())
            for row_key in sorted_rows:
                pfr = epoch.pfe_pfr_map[row_key]
                for peaker in self._bin_peakers(pfr.samples_list):
                    sample_frequency = peaker[0]
                    if sample_frequency not in discovered_map:
                        discovered_map[sample_frequency] = peaker
                    elif discovered_map[sample_frequency][1] < peaker[1]:
                        discovered_map[sample_frequency] = peaker

        return [discovered_map[key] for key in sorted(discovered_map.keys())]

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***

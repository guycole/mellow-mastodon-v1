#
# Title: power_peaker.py
# Description: discover signal peakers
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#
import numpy as np
from typing import Any

Peaker = list[float]


class PowerPeaker:
    HALF_WINDOW_SIZE = 33
    GUARD_WINDOW_SIZE = 4
    SIGMA_MULTIPLIER = 5.0
    MINIMUM_DELTA_DB = 6.0
    MINIMUM_SIGMA_DB = 0.5

    def __init__(self, power_epoch_map: dict[int, Any]):
        self.power_epoch_map = power_epoch_map

    def _bin_peakers(self, samples_list: list[tuple[int, float]]) -> list[Peaker]:
        if not samples_list:
            return []

        freqs = np.array([s[0] for s in samples_list], dtype=np.int64)
        values = np.array([s[1] for s in samples_list])
        n = len(values)
        row_baseline = np.median(values)
        result: list[Peaker] = []

        half = self.HALF_WINDOW_SIZE
        guard = self.GUARD_WINDOW_SIZE

        for ndx in range(n):
            ls = max(0, ndx - half)
            le = max(ls, ndx - guard)
            rs = min(n, ndx + guard + 1)
            re = min(n, ndx + half + 1)
            training = np.concatenate([values[ls:le], values[rs:re]])
            if len(training) < 4:
                training = np.delete(values, ndx)

            local_baseline = np.median(training) if len(training) else row_baseline
            local_mad = (
                np.median(np.abs(training - local_baseline)) if len(training) else 0.0
            )
            local_sigma = max(1.4826 * local_mad, self.MINIMUM_SIGMA_DB)
            detection_threshold = local_baseline + max(
                self.MINIMUM_DELTA_DB, self.SIGMA_MULTIPLIER * local_sigma
            )

            if values[ndx] > detection_threshold:
                result.append(
                    [int(freqs[ndx]), float(values[ndx]), float(local_baseline)]
                )

        return result

    def discover_peakers(self) -> list[Peaker]:
        discovered_map: dict[int, Peaker] = {}

        for epoch_key in sorted(self.power_epoch_map.keys()):
            epoch_data = self.power_epoch_map[epoch_key]
            for row_key in sorted(epoch_data.keys()):
                for peaker in self._bin_peakers(epoch_data[row_key]):
                    sample_frequency = peaker[0]
                    if sample_frequency not in discovered_map:
                        discovered_map[sample_frequency] = peaker
                    elif discovered_map[sample_frequency][1] < peaker[1]:
                        discovered_map[sample_frequency] = peaker

        return [discovered_map[key] for key in sorted(discovered_map.keys())]


# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***

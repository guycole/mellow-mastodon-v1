#
# Title: power_file.py
# Description: process a rtl_power CSV file
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#
import logging

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("power_file")


class PowerFile:
    def __init__(self, file_name: str):
        self.file_name = file_name

    def parser(self) -> dict[int, dict[int, list[tuple[int, float]]]]:
        """Read rtl_power CSV and return {epoch: {freq_low_hz: [(freq_hz, dbm), ...]}}"""

        df = pd.read_csv(self.file_name, header=None)

        timestamps = pd.to_datetime(
            df[0].str.strip() + " " + df[1].str.strip(),
            format="%Y-%m-%d %H:%M:%S",
        )
        epochs = (timestamps.astype(np.int64) // 10**9).values

        freq_lows = df[2].values.astype(np.int64)
        freq_highs = df[3].values.astype(np.int64)
        freq_steps = df[4].values.astype(float)
        dbm_data = df.iloc[:, 6:].values.astype(float)

        power_epoch_map: dict[int, dict[int, list[tuple[int, float]]]] = {}

        for i in range(len(epochs)):
            epoch_key = int(epochs[i])
            freq_low = int(freq_lows[i])
            freq_step = float(freq_steps[i])

            dbm_row = dbm_data[i]
            dbm_values = dbm_row[~np.isnan(dbm_row)]
            n = len(dbm_values)
            if n == 0:
                continue

            freqs = (freq_low + np.arange(n) * freq_step).astype(np.int64)

            if int(freqs[-1]) != int(freq_highs[i]):
                logger.warning(
                    "frequency mismatch at row %s: %s != %s",
                    i,
                    freqs[-1],
                    freq_highs[i],
                )

            samples = list(zip(freqs.tolist(), dbm_values.tolist()))

            if epoch_key not in power_epoch_map:
                power_epoch_map[epoch_key] = {}
            power_epoch_map[epoch_key][freq_low] = samples

        return power_epoch_map


# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***

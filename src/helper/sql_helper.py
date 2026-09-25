#
# Title: sql_helper.py
# Description: 
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#

import logging

import datetime

from helper.postgres import PostGres

logger = logging.getLogger("sql_helper")

class SqlHelper:

    def __init__(self, postgres: PostGres, jh, source_logger: logging.Logger | None = None):
        self.postgres = postgres
        self.jh = jh
        self.logger = source_logger or logger

    def _job_task(self) -> str:
        task = self.jh.raw_json.get("job", {}).get("task")
        if isinstance(task, str):
            task = task.strip()

        if task:
            return task

        raise ValueError("job.task must be a non-empty string")

    def load_log_test(self, test_file_name: str) -> int:
        self.logger.info(f"load_log_test for file: {test_file_name}")

        try:
            candidate = self.postgres.load_log_select_by_file_name(test_file_name)
            if candidate is None:
                self.logger.info(f"processing new file:{test_file_name}")
                task = self._job_task()

                geo_loc = self.postgres.geo_loc_select_by_site(self.jh.raw_json["geoLoc"]["siteName"])
                if len(geo_loc) == 0:
                    print("must insert geo_loc for site:", self.jh.raw_json["geoLoc"]["siteName"])
                    return 0

                load_log = {
                    "crate_name": self.jh.raw_json["crateName"],
                    "epoch_seconds": self.jh.raw_json["timeStamp"]["epochSeconds"],
                    "file_name": test_file_name,
                    "geo_loc_id": geo_loc[0].id,
                    "host_name": self.jh.raw_json["equipment"]["hostName"],
                    "load_time": datetime.datetime.now(),
                    "mode": self.jh.raw_json["job"]["mode"],
                    "obs_time": self.jh.raw_json["timeStamp"]["iso8601"],
                    "peaker_quantity": len(self.jh.raw_json["peakers"]),
                    "site_name": self.jh.raw_json["geoLoc"]["siteName"],
                    "task": task,
                }

                inserted = self.postgres.load_log_insert(load_log)

                if inserted is None or inserted.id is None:
                    # Insert failed (for example unique-key collision); signal caller to skip obs load.
                    self.logger.warning(
                        "load_log insert did not return an id for %s", test_file_name
                    )
                    return 0

                daily_score = {
                    "crate_name": self.jh.raw_json["crateName"],
                    "file_quantity": 1,
                    "host_name": self.jh.raw_json["equipment"]["hostName"],
                    "peaker_quantity": len(self.jh.raw_json["peakers"]),
                    "score_date": datetime.date.fromisoformat(self.jh.raw_json["timeStamp"]["iso8601"][:10]),
                    "task": task,
                }

                self.postgres.daily_score_insert_or_update(daily_score)

                if len(self.jh.raw_json["peakers"]) < 1:
                    self.logger.info("skipping file with no peakers")
                    return 0

                return inserted.id

            self.logger.info(f"skippping already processed:{test_file_name}")
        except Exception as error:
            self.logger.error(f"postgres insert failed for {test_file_name}: {error}")

        return 0

    def load_obs(self, load_log_id: int) -> bool:
        if load_log_id is None or load_log_id < 1:
            self.logger.error("load_log_id is not set")
            return False

        task = self._job_task()

        def _peaker_values(observation):
            if isinstance(observation, dict):
                return (
                    int(observation["frequency_hz"]),
                    float(observation["measured_dbm"]),
                    float(observation["background_dbm"]),
                )

            if isinstance(observation, (list, tuple)) and len(observation) == 3:
                return (
                    int(observation[0]),
                    float(observation[1]),
                    float(observation[2]),
                )

            raise ValueError(f"invalid peaker observation shape: {observation}")
        
        try:
            for observation in self.jh.raw_json["peakers"]:
                freq_hz, power_dbm, baseline_dbm = _peaker_values(observation)

                obs = {
                    "baseline_dbm": baseline_dbm,
                    "freq_hz": freq_hz,
                    "load_log_id": load_log_id,
                    "power_dbm": power_dbm,
                }

                self.postgres.observation_insert(obs)

                score = {
                    "crate_name": self.jh.raw_json["crateName"],
                    "freq_hz": freq_hz,
                    "peaker_quantity": 1,
                    "task": task,
                }

                self.postgres.peaker_score_insert_or_update(score)

            return True
        except Exception as error:
            self.logger.error(f"observation insert failed for load_log_id {load_log_id}: {error}")

        return False

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***

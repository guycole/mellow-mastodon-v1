#
# Title: loader.py
# Description: load mastodon files
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#
import logging
import json
import os

from helper.json_helper import JsonHelper, schema

from helper.postgres import PostGres
from helper.sql_helper import SqlHelper

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("loader")

class Loader:

    def __init__(self, postgres: PostGres):
        self.postgres = postgres

        self.failure_dir = os.environ.get("FAILURE_DIR", "/var/peccary/mastodon/failure")
        self.fresh_dir = os.environ.get("FRESH_DIR", "/var/peccary/mastodon/mastodon-v1")

        self.failure = 0
        self.success = 0

        self.jh = JsonHelper()
        self.sql_helper = SqlHelper(self.postgres, self.jh, logger)

    def file_failure(self, file_name: str):
        #        logger.info(f"file failure:{file_name}")

        self.failure += 1
        os.rename(file_name, self.failure_dir + "/" + file_name)

    def file_success(self, file_name: str):
        #        logger.info(f"file success:{file_name}")

        self.success += 1
        os.remove(file_name)

    def _job_task(self) -> str:
        task = self.jh.raw_json.get("job", {}).get("task")
        if isinstance(task, str):
            task = task.strip()

        if task:
            return task

        raise ValueError("job.task must be a non-empty string")

    def load_log_test(self, test_file_name: str) -> bool:
        status = self.sql_helper.load_log_test(test_file_name, capture_load_log_id=True)
        self.load_log_id = self.sql_helper.load_log_id

        return status

    def file_processor(self, file_name) -> None:
        logger.info(f"processing file: {file_name}")
        
        if not self.jh.json_file_tester(file_name):
            self.file_failure(file_name)
            return

        load_log_id = self.sql_helper.load_log_test(file_name)
        if load_log_id < 1:
            self.file_failure(file_name)
            return

        if self.load_obs(load_log_id):
            pass
        else:
            self.file_failure(file_name)
            return

        self.file_success(file_name)

    def execute(self) -> None:
        logger.info(f"loader fresh dir:{self.fresh_dir}")

        os.chdir(self.fresh_dir)
        targets = sorted(os.listdir("."))
        logger.info(f"{len(targets)} files noted")

        for target in targets:
            self.file_processor(target)

        logger.info(f"loader success:{self.success} failure:{self.failure}")

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***

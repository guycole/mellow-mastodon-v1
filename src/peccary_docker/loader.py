#
# Title: loader.py
# Description: load mastodon files
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#
import logging
import os

from helper.json_helper import JsonHelper
from helper.postgres import PostGres
from helper.sql_helper import SqlHelper

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("loader")


class Loader:
    """Loader for mastodon files, aligned to slug loader control flow."""

    def __init__(self, postgres: PostGres):
        self.postgres = postgres

        self.failure_dir = os.environ.get("FAILURE_DIR", "/var/peccary/mastodon/failure")
        self.fresh_dir = os.environ.get("FRESH_DIR", "/var/peccary/mastodon/mastodon-v1")

        self.failure = 0
        self.success = 0

        self.jh = JsonHelper()
        self.sql_helper = SqlHelper(self.postgres, self.jh, logger)

    def file_failure(self, file_name: str) -> None:
        logger.info("file failure:%s", file_name)

        self.failure += 1
        failure_target = os.path.join(self.failure_dir, file_name)
        try:
            os.rename(file_name, failure_target)
        except Exception as error:
            logger.error(
                "file move failure for %s -> %s: %s",
                file_name,
                failure_target,
                error,
            )

    def file_success(self, file_name: str) -> None:
        logger.info("file success:%s", file_name)

        self.success += 1
        try:
            os.remove(file_name)
        except Exception as error:
            logger.error("file delete failure for %s: %s", file_name, error)

    def file_processor(self, file_name: str) -> bool:
        logger.info("processing file:%s", file_name)

        if not self.jh.json_file_tester(file_name):
            self.file_failure(file_name)
            return False

        load_log_id = self.sql_helper.load_log_test(file_name)
        if load_log_id < 1:
            self.file_failure(file_name)
            return False

        if not self.sql_helper.load_obs(load_log_id):
            self.file_failure(file_name)
            return False

        self.file_success(file_name)
        return True

    def execute(self) -> int:
        logger.info("loader fresh dir:%s", self.fresh_dir)

        os.chdir(self.fresh_dir)
        targets = sorted(os.listdir("."))
        logger.info("%s files noted", len(targets))

        for target in targets:
            self.file_processor(target)

        logger.info("loader success:%s failure:%s", self.success, self.failure)

        return 0

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***

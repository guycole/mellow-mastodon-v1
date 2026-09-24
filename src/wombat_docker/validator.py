#
# Title: validator.py
# Description: ensure valid mastodon files
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#
import logging
import os
from collections import defaultdict
from abc import ABC, abstractmethod

from helper.json_helper import JsonHelper
from helper.postgres import PostGres
from helper.sql_helper import SqlHelper

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("validator")


class Validator(ABC):
    @abstractmethod
    def file_processor(self, gp_file_name: str, json_file_name: str) -> None:
        pass

    @abstractmethod
    def execute(self) -> int:
        pass

    @abstractmethod
    def file_failure(self, file_name: str) -> None:
        pass

    @abstractmethod
    def file_success(self, file_name: str) -> None:
        pass


class MastodonValidator(Validator):
    def __init__(self, postgres: PostGres):
        self.postgres = postgres

        self.failure_dir = os.environ.get("FAILURE_DIR", "/var/wombat/failure")
        self.fresh_dir = os.environ.get("FRESH_DIR", "/var/wombat/fresh/mastodon")
        self.success_dir = os.environ.get("SUCCESS_DIR", "/var/wombat/mastodon/success")

        self.failure = 0
        self.success = 0

        self.jh = JsonHelper()
        self.sql_helper = SqlHelper(self.postgres, self.jh, logger)

    def _move_file(self, file_name: str, target_dir: str) -> bool:
        source = os.path.abspath(file_name)
        target = os.path.join(target_dir, file_name)

        try:
            os.rename(source, target)
        except Exception as error:
            logger.error("file move failure for %s -> %s: %s", source, target, error)
            return False

        return True

    def file_failure(self, file_name: str) -> None:
        logger.info("file failure:%s", file_name)

        self.failure += 1
        self._move_file(file_name, self.failure_dir)

    def file_success(self, file_name: str) -> None:
        logger.info("file success:%s", file_name)

        self.success += 1
        self._move_file(file_name, self.success_dir)

    def file_failure_pair(self, file_name1: str, file_name2: str) -> None:
        self.file_failure(file_name1)
        self.file_failure(file_name2)

    def file_success_pair(self, file_name1: str, file_name2: str) -> None:
        self.file_success(file_name1)
        self.file_success(file_name2)

    @staticmethod
    def _paired_targets(targets: list[str]) -> tuple[list[tuple[str, str]], list[str]]:
        grouped: dict[str, set[str]] = defaultdict(set)
        for target in targets:
            base_name, extension = os.path.splitext(target)
            if extension:
                grouped[base_name].add(extension.lower())

        pairs: list[tuple[str, str]] = []
        unpaired: list[str] = []

        for base_name in sorted(grouped.keys()):
            expected = {".gp", ".json"}
            if grouped[base_name] == expected:
                pairs.append((f"{base_name}.gp", f"{base_name}.json"))
            else:
                for extension in sorted(grouped[base_name]):
                    unpaired.append(f"{base_name}{extension}")

        return pairs, unpaired

    def file_processor(self, gp_file_name: str, json_file_name: str) -> None:
        logger.info("processing files: %s %s", gp_file_name, json_file_name)

        if not self.jh.json_file_tester(json_file_name):
            logger.warning("file read failed for %s", json_file_name)
            self.file_failure_pair(gp_file_name, json_file_name)
            return

        load_log_id = self.sql_helper.load_log_test(json_file_name)
        if load_log_id < 1:
            self.file_failure_pair(gp_file_name, json_file_name)
            return

        if not self.sql_helper.load_obs(load_log_id):
            self.file_failure_pair(gp_file_name, json_file_name)
            return

        self.file_success_pair(gp_file_name, json_file_name)

    def execute(self) -> int:
        logger.info("validator fresh dir:%s", self.fresh_dir)

        os.chdir(self.fresh_dir)
        targets = sorted(os.listdir("."))
        logger.info("%s files noted", len(targets))

        pairs, unpaired = self._paired_targets(targets)
        for target in unpaired:
            logger.info("unpaired target noted: %s", target)
            self.file_failure(target)

        for gp_file_name, json_file_name in pairs:
            self.file_processor(gp_file_name, json_file_name)

        logger.info("validator success:%s failure:%s", self.success, self.failure)
        return 0

# Keep import compatibility for existing tests/callers.
Validator = MastodonValidator

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***

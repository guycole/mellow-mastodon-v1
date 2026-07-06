#
# Title: validator.py
# Description: ensure valid mastodon files
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#
import logging
import datetime
import json
import os
import time

from postgres import PostGres

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("mastodon")

class Validator:

    def __init__(self, postgres: PostGres):
        self.postgres = postgres

        # path from inside docker container
        self.failure_dir = "/mnt/wombat/failure/"
        self.fresh_dir = "/mnt/wombat/fresh/mastodon"
        self.success_dir = "/mnt/wombat/mastodon/success/"

        # path for mac development
        # self.failure_dir = "/var/wombat/failure/"
        # self.fresh_dir = "/var/wombat/fresh/mastodon"
        # self.success_dir = "/var/wombat/mastodon/success/"

        self.failure = 0
        self.success = 0

    def file_failure(self, file_name: str):
        logger.info(f"file failure:{file_name}")

        self.failure += 1
        os.rename(file_name, self.failure_dir + file_name)

    def file_success(self, file_name1: str, file_name2: str):
        #logger.info(f"file success:{file_name1}, {file_name2}")

        self.success += 1
        os.rename(file_name1, self.success_dir + "/" + file_name1)
        os.rename(file_name2, self.success_dir + "/" + file_name2)

    def file_reader(self, file_name: str) -> bool:
        try:
            with open(file_name, "r", encoding="utf-8") as in_file:
                self.raw_buffer = json.load(in_file)
        except Exception as error:
            logger.error(f"file read failed for {file_name}: {error}")
            return False

        return True

    def load_log_test(self, test_file_name: str) -> bool:
        try:
            candidate = self.postgres.load_log_select_by_file_name(test_file_name)
            if candidate is not None:
                logger.info(f"skippping already processed:{test_file_name}")
                return False
            else:
                load_log = {
                    "file_name": test_file_name,
                    "host_name": self.raw_buffer["equipment"]["hostName"],
                    "obs_time": self.raw_buffer["timeStamp"]["iso8601"],
                    "project": self.raw_buffer["project"],
                }

                self.postgres.load_log_insert(load_log)

                return True
        except Exception as error:
            logger.error(f"postgres insert failed for {test_file_name}: {error}")        
        
        return False

    def file_processor(self, file_name1: str, file_name2: str) -> None:
        if os.path.isfile(file_name1) is False:
            logger.warning(f"skipping non-file:{file_name1}")
            self.file_failure(file_name1)
            self.file_failure(file_name2)
            return

        if os.path.isfile(file_name2) is False:
            logger.warning(f"skipping non-file:{file_name2}")
            self.file_failure(file_name1)
            self.file_failure(file_name2)
            return
        
        test_file_name = file_name1 if file_name1.endswith(".json") else file_name2
        if not self.file_reader(test_file_name):
            logger.warning(f"file read failed for {test_file_name}")
            self.file_failure(file_name1)
            self.file_failure(file_name2)
            return
       
        if self.raw_buffer["version"] == 1 and self.raw_buffer["project"] == "mastodon-v1-bs1":
            pass
        else:
            logger.warning(f"invalid version or project for {test_file_name} {self.raw_buffer['project']}")
            self.file_failure(file_name1)
            self.file_failure(file_name2)
            return
        
        if self.load_log_test(test_file_name):
            self.file_success(file_name1, file_name2)
        else:
            self.file_failure(file_name1)
            self.file_failure(file_name2)

    def execute(self) -> None:
        logger.info("validator")
        logger.info(f"fresh dir:{self.fresh_dir}")

        os.chdir(self.fresh_dir)
        targets = sorted(os.listdir("."))
        logger.info(f"{len(targets)} files noted")
        if len(targets) < 2:
            return

        time_now = int(time.time())
        threshold = 60 * 10 # 10 minutes

        # mastodon files arrive in pairs: one .json and one .csv file sharing
        # the same base name.  The files will not arrive at the same time, so 
        # if one file is missing I need to wait for the late file to arrive.
        # I iterate through sorted filenames to discover matching pairs.
        # Files are given ten minutes to arrive.

        ndx1 = 0
        while ndx1 < len(targets)-1:
            # valid files will arrive in pairs
            target1 = targets[ndx1]
            target2 = targets[ndx1+1]
            print(f"testing {target1} {target2}")

            target1_mtime = os.path.getmtime(target1)
            delta1 = time_now - target1_mtime

            target2_mtime = os.path.getmtime(target2)
            delta2 = time_now - target2_mtime

            temp = target1.split(".")
            if target2.startswith(temp[0]):
                print("filenames match") 
                if delta1 > threshold and delta2 > threshold:
                    print("process ripe files")
                    self.file_processor(target1, target2)
                    ndx1 += 1
                else:
                    print(f"skip unripe file")
                    ndx1 += 1  # skip both files of the unripe pair
            else:
                print(f"filenames do not match")
                if delta1 > threshold:
                    self.file_failure(target1)

            ndx1 += 1

        logger.info(f"validator success:{self.success} failure:{self.failure}")

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***

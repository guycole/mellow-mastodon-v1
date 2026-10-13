#
# Title: loader.py
# Description: parse mellow mastodon files and load to postgresql
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#
import datetime
import os
import shutil
import sys

import yaml
from yaml.loader import SafeLoader

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import postgres

from mastodon_file import MastodonFile


class Loader:
    def __init__(self, configuration: dict[str, str]):
        self.failure_dir = configuration["failureDir"]
        self.peaker_dir = configuration["peakerDir"]

        self.db_conn = configuration["dbConn"]
        self.sql_echo = configuration["sqlEchoEnable"]

        connect_dict = {"options": "-csearch_path={}".format("mastodon_v1")}
        db_engine = create_engine(
            self.db_conn, echo=self.sql_echo, connect_args=connect_dict
        )

        self.postgres = postgres.PostGres(
            sessionmaker(bind=db_engine, expire_on_commit=False)
        )

        self.failure_counter = 0
        self.success_counter = 0

    def file_success(self, file_name: str):
        """file was successfully processed"""

        self.success_counter += 1

        os.unlink(file_name)

    def file_failure(self, file_name: str):
        """problem file, retain for review"""

        self.failure_counter += 1

        print(f"failure move for {file_name}")

        shutil.move(file_name, self.failure_dir + "/" + file_name)
        # os.rename(file_name, self.failure_dir + "/" + file_name)

    def execute(self) -> None:
        mastodon_file = MastodonFile(self.postgres)

        print(f"peaker dir:{self.peaker_dir}")
        os.chdir(self.peaker_dir)

        targets = os.listdir(".")
        print(f"{len(targets)} files noted")

        for target in targets:
            print(f"processing {target}")

            if os.path.isfile(target) is False:
                print(f"skipping {target}")
                continue

            status = mastodon_file.processor(target)
            if status is True:
                self.file_success(target)
            else:
                self.file_failure(target)

        print(f"success:{self.success_counter} failure:{self.failure_counter}")


print("start loader")

#
# argv[1] = configuration filename
#
if __name__ == "__main__":
    if len(sys.argv) > 1:
        config_name = sys.argv[1]
    else:
        config_name = "config.yaml"

    with open(config_name, "r", encoding="utf-8") as in_file:
        try:
            configuration = yaml.load(in_file, Loader=SafeLoader)
        except yaml.YAMLError as error:
            print(error)

    loader = Loader(configuration)
    loader.execute()

print("stop loader")

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***

#
# Title: case_dump.py
# Description: update catalog files
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#
import sys
import uuid

import yaml
from yaml.loader import SafeLoader

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import json_helper
import postgres

from sql_table import Population, Site


class CaseDump:
    default_case_uuid = "10514480-5caf-4a41-98f2-a57eb24c2f9b"

    def __init__(self, configuration: dict[str, str]):
        self.case_dir = configuration["caseDir"]

        self.db_conn = configuration["dbConn"]
        self.sql_echo = configuration["sqlEchoEnable"]

        self.population_threshold = configuration["populationThreshold"]

        connect_dict = {"options": "-csearch_path={}".format("mastodon_v1")}
        db_engine = create_engine(
            self.db_conn, echo=self.sql_echo, connect_args=connect_dict
        )

        self.postgres = postgres.PostGres(
            sessionmaker(bind=db_engine, expire_on_commit=False)
        )

    def create_fresh_case(self, bin: Population, site: Site) -> None:
        bin.case_uuid = str(uuid.uuid4())
        self.postgres.population_update(bin)

        helper = json_helper.JsonHelper(self.case_dir)
        payload = helper.fresh_population_to_json(bin, "big-search01", site)
        helper.json_writer(payload)

    def update_existing_case(self, bin: Population, site: Site) -> None:
        helper = json_helper.JsonHelper(self.case_dir)

        payload = helper.json_reader(bin.case_uuid)
        if len(payload) < 1:
            print(f"case {bin.case_uuid} read error")
            self.create_fresh_case(bin, site)
            return

        payload["obsFirstEpochTime"] = int(bin.obs_first.timestamp())
        payload["obsLastEpochTime"] = int(bin.obs_last.timestamp())

        helper.json_writer(payload)

    def process_site_population(self, site: Site) -> None:
        print(f"process {site}")

        below_threshold = 0
        existing_case = 0
        fresh_case = 0

        population_list = self.postgres.population_select_all_by_site(site.id)
        for bin in population_list:
            print(
                f"bin population: {bin.case_uuid} {bin.population} threshold: {self.population_threshold}"
            )
            if bin.population < self.population_threshold:
                below_threshold = below_threshold + 1
                continue

            if bin.case_uuid == self.default_case_uuid:
                fresh_case = fresh_case + 1
                self.create_fresh_case(bin, site)
            else:
                existing_case = existing_case + 1
                self.update_existing_case(bin, site)

        print(
            f"site {site.name} below {below_threshold} existing {existing_case} fresh {fresh_case}"
        )

    def execute(self) -> None:
        site_list = self.postgres.site_select_all()

        for site in site_list:
            self.process_site_population(site)


print("start case_dump")

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

    dumper = CaseDump(configuration)
    dumper.execute()

print("stop case_dump")

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***

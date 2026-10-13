#
# Title: case_fix.py
# Description: read a case and update the database
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#
import sys

import yaml
from yaml.loader import SafeLoader

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import json_helper
import postgres

from sql_table import Equipment, LoadLog, Observation, Population, Site


class CaseFix:
    default_case_uuid = "10514480-5caf-4a41-98f2-a57eb24c2f9b"

    def __init__(self, configuration: dict[str, str]):
        self.case_dir = configuration["caseDir"]

        self.db_conn = configuration["dbConn"]
        self.sql_echo = configuration["sqlEchoEnable"]

        connect_dict = {"options": "-csearch_path={}".format("mastodon_v1")}
        db_engine = create_engine(
            self.db_conn, echo=self.sql_echo, connect_args=connect_dict
        )

        self.postgres = postgres.PostGres(
            sessionmaker(bind=db_engine, expire_on_commit=False)
        )

    def execute(self, case_uuid: str) -> None:
        print(f"case_fix {case_uuid}")

        # read case card
        helper = json_helper.JsonHelper(self.case_dir)
        case_card = helper.json_reader(case_uuid)
        if len(case_card) < 1:
            print(f"case {case_uuid} not found")
            return
        
        site = self.postgres.site_select_by_name(case_card['obsSite'])
        if site is None:
            print(f"site {case_card['obsSite']} not found")
            return

        # select population entry for each freq bin
        for bin in case_card["freqBins"]:
            print(f"update {bin}")

            candidates = self.postgres.population_select_by_frequency_site_id(
                bin, site.id
            )
            if len(candidates) != 1:
                print(f"population entry not found for {bin} {site}")
                continue

            # update case uuid within postgres for this bin
            candidates[0].case_uuid = case_uuid
            self.postgres.population_update(candidates[0])


print("start casefix")

#
# argv[1] = case uuid
# argv[2] = configuration filename
#
if __name__ == "__main__":
    case_uuid = sys.argv[1]

    if len(sys.argv) > 2:
        config_name = sys.argv[2]
    else:
        config_name = "config.yaml"

    with open(config_name, "r", encoding="utf-8") as in_file:
        try:
            configuration = yaml.load(in_file, Loader=SafeLoader)
        except yaml.YAMLError as error:
            print(error)

    casefix = CaseFix(configuration)
    casefix.execute(case_uuid)

print("stop casefix")

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***

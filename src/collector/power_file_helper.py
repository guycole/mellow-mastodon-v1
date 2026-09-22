#
# Title: power_file_helper.py
# Description: mastodon utility classes
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#
import csv


class PowerFileHelper:
    def csv_file_reader(self, file_name: str) -> list[list[str]]:
        """read mastodon csv file and return list of rows"""

        result = []

        try:
            with open(file_name, "r", encoding="utf-8", newline="") as in_file:
                csv_file = csv.reader(in_file)
                for row in csv_file:
                    result.append(row)
        except Exception as error:
            print(error)

        return result


# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***

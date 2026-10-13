#
# Title: test_helper.py
# Description:
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#
from power_file_helper import MastodonHelper

from unittest import TestCase


class TestHelper(TestCase):
    def test1(self):
        filename = "../test/big-search-000774db-0f2d-47cc-b966-c52abb61a5ef.anderson1"

        helper = MastodonHelper()
        result = helper.csv_file_reader(filename)
        self.assertTrue(result)


# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***

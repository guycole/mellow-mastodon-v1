#
# Title: test_row.py
# Description:
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#
import os

from mastodon_row import MastodonRow

from unittest import TestCase


class TestRow(TestCase):
    def test1(self):
        """bad file name formats"""

        result = None

        try:
            file_name = "bogus"
            result = MastodonRow(file_name)
        except Exception as error:
            print(f"bad name 1: {error}")

        self.assertIsNone(result)

        try:
            file_name = "bogus.bogus"
            result = MastodonRow("bogus.bogus")
        except Exception as error:
            print(f"bad name 2: {error}")

        self.assertIsNone(result)

    def test2(self):
        """good file name formats"""

        result = None

        try:
            file_name = "big-search-000774db-0f2d-47cc-b966-c52abb61a5ef.anderson1"
            result = MastodonRow(file_name)
        except Exception as error:
            print(f"bad name 1: {error}")

        self.assertIsNotNone(result)

    def test3(self):
        """row meta and sample parsing"""

        file_name = "big-search-000774db-0f2d-47cc-b966-c52abb61a5ef.anderson1"
        result = MastodonRow(file_name)

        row_data = [
            "2025-07-27",
            "20:36:05",
            "120772425",
            "123569849",
            "2731.86",
            "13",
            "-1.0",
            "-3.0",
            "-5.0",
            "-7.0",
            "-9.0",
        ]
        result.row_meta(row_data)

        self.assertEqual(result._header["meta"]["freq_low_hz"], 120772425)
        self.assertEqual(result._header["meta"]["freq_high_hz"], 123569849)
        self.assertEqual(result._header["meta"]["freq_step_hz"], 2731.86)
        self.assertEqual(result._header["meta"]["time_stamp_epoch"], 1753673765)
        self.assertEqual(
            result._header["meta"]["time_stamp_iso8601"], "2025-07-27T20:36:05"
        )
        self.assertEqual(result._header["meta"]["sample_quantity"], 13)

        result.row_samples(row_data)

        self.assertEqual(len(result._header["samples"]), 5)
        self.assertEqual(result._header["statistics"]["avg_sample"], -5.0)
        self.assertEqual(result._header["statistics"]["min_sample"], -9.0)
        self.assertEqual(result._header["statistics"]["max_sample"], -1.0)


#    def test4(self):
#        """ row energy detection """
#
#        os.chdir("../test")
#
#        file_name = "big-search-000774db-0f2d-47cc-b966-c52abb61a5ef.anderson1"
#        result = MastodonRow(file_name)
#
#        self.assertIsNone(result)
#
#        result.row_energy()

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***

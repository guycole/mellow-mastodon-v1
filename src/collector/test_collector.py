import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"
COLLECTOR_DIR = SRC_DIR / "collector"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

if str(COLLECTOR_DIR) not in sys.path:
    sys.path.insert(0, str(COLLECTOR_DIR))

from collector import Collector
from helper.json_helper import schema
from jsonschema import validate


class TestCollector(unittest.TestCase):
    SAMPLE_BASE_NAME = "dd9a208e-f890-4098-ab0f-9264eef1c371"
    SAMPLE_SOURCE = ROOT_DIR / "samples" / f"{SAMPLE_BASE_NAME}.csv"
    SAMPLE_TMP = Path("/tmp") / f"{SAMPLE_BASE_NAME}.csv"

    def _collector_args(self, fresh_dir: str) -> dict[str, Any]:
        return {
            "crateName": "unit-test-crate",
            "freshDir": fresh_dir,
            "equipment": {
                "hostName": "unit-host",
                "hostType": "rpi",
            },
            "geoLoc": {
                "altitude": 1.0,
                "latitude": 2.0,
                "longitude": 3.0,
                "siteName": "unit-site",
            },
            "receiver": {
                "antenna": "unit-antenna",
                "receiverId": 1,
                "task": "anderson-bs1-pk1",
                "type": "rtl-sdr",
            },
        }

    def test_execute_creates_json_with_same_basename(self) -> None:
        self.assertTrue(
            self.SAMPLE_SOURCE.exists(), f"missing sample: {self.SAMPLE_SOURCE}"
        )

        shutil.copyfile(self.SAMPLE_SOURCE, self.SAMPLE_TMP)
        self.addCleanup(lambda: self.SAMPLE_TMP.exists() and self.SAMPLE_TMP.unlink())

        with tempfile.TemporaryDirectory() as fresh_dir:
            collector = Collector(self._collector_args(fresh_dir))
            start_time = 1750000000

            collector.execute(self.SAMPLE_BASE_NAME, start_time)

            output_path = Path(fresh_dir) / f"{self.SAMPLE_BASE_NAME}.json"
            self.assertTrue(output_path.exists(), f"missing output: {output_path}")

            with open(output_path, "r", encoding="utf-8") as in_file:
                payload = json.load(in_file)

            validate(instance=payload, schema=schema)

            self.assertEqual(payload["fileName"], f"{self.SAMPLE_BASE_NAME}.json")
            self.assertEqual(payload["crateName"], "unit-test-crate")
            self.assertEqual(payload["job"]["task"], "anderson-bs1-pk1")
            self.assertEqual(payload["timeStamp"]["epochSeconds"], start_time)
            self.assertIsInstance(payload["peakers"], list)

    def test_execute_missing_csv_does_not_create_output(self) -> None:
        missing_base = "collector-unit-missing-input"
        missing_csv = Path("/tmp") / f"{missing_base}.csv"
        if missing_csv.exists():
            missing_csv.unlink()

        with tempfile.TemporaryDirectory() as fresh_dir:
            collector = Collector(self._collector_args(fresh_dir))
            collector.execute(missing_base, 1750000000)

            output_path = Path(fresh_dir) / f"{missing_base}.json"
            self.assertFalse(output_path.exists(), f"unexpected output: {output_path}")


if __name__ == "__main__":
    unittest.main()

import logging

from validator import Validator


class FakeSqlHelper:
    def __init__(self):
        self.load_log_id = 7
        self.load_obs_result = True

    def load_log_test(self, _file_name: str) -> int:
        return self.load_log_id

    def load_obs(self, _load_log_id: int) -> bool:
        return self.load_obs_result


class FakeJsonHelper:
    def __init__(self):
        self.result = True

    def json_file_tester(self, _file_name: str) -> bool:
        return self.result


class FakePostgres:
    pass


def _validator() -> Validator:
    validator = Validator(FakePostgres())
    validator.jh = FakeJsonHelper()
    validator.sql_helper = FakeSqlHelper()
    validator.failure_dir = "/tmp/failure"
    validator.success_dir = "/tmp/success"
    return validator


def test_paired_targets_detects_pairs_and_unpaired() -> None:
    pairs, unpaired = Validator._paired_targets(
        ["a.csv", "a.json", "b.json", "c.csv", "d.txt"]
    )

    assert pairs == [("a.csv", "a.json")]
    assert unpaired == ["b.json", "c.csv", "d.txt"]


def test_file_processor_success_path(monkeypatch) -> None:
    validator = _validator()

    calls = {"success": 0, "failure": 0}
    monkeypatch.setattr(
        validator,
        "file_success_pair",
        lambda _csv, _json: calls.__setitem__("success", calls["success"] + 1),
    )
    monkeypatch.setattr(
        validator,
        "file_failure_pair",
        lambda _csv, _json: calls.__setitem__("failure", calls["failure"] + 1),
    )

    validator.file_processor("a.csv", "a.json")

    assert calls["success"] == 1
    assert calls["failure"] == 0


def test_file_processor_validation_failure(monkeypatch) -> None:
    validator = _validator()
    validator.jh.result = False

    calls = {"success": 0, "failure": 0}
    monkeypatch.setattr(
        validator,
        "file_success_pair",
        lambda _csv, _json: calls.__setitem__("success", calls["success"] + 1),
    )
    monkeypatch.setattr(
        validator,
        "file_failure_pair",
        lambda _csv, _json: calls.__setitem__("failure", calls["failure"] + 1),
    )

    validator.file_processor("a.csv", "a.json")

    assert calls["success"] == 0
    assert calls["failure"] == 1


def test_execute_processes_pairs_and_unpaired(monkeypatch) -> None:
    validator = _validator()

    monkeypatch.setattr("validator.os.chdir", lambda _path: None)
    monkeypatch.setattr("validator.os.listdir", lambda _path: ["b.json", "a.csv", "a.json"])

    processed = []
    failed = []
    monkeypatch.setattr(
        validator,
        "file_processor",
        lambda csv_name, js: processed.append((csv_name, js)),
    )
    monkeypatch.setattr(
        validator,
        "file_failure",
        lambda name: failed.append(name),
    )

    validator.execute()

    assert processed == [("a.csv", "a.json")]
    assert failed == ["b.json"]

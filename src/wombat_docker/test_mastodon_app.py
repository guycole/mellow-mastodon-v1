import mastodon_app


def test_execute_runs_validator_mode(monkeypatch) -> None:
    class FakeValidator:
        def __init__(self, _postgres):
            pass

        def execute(self) -> None:
            return None

    monkeypatch.setattr(mastodon_app, "Validator", FakeValidator)

    app = mastodon_app.MastodonApp("validator")

    assert app.execute() == 0


def test_execute_runs_koala_mode(monkeypatch) -> None:
    class FakeKoala:
        def execute(self) -> None:
            return None

    monkeypatch.setattr(mastodon_app, "Koala", FakeKoala)

    app = mastodon_app.MastodonApp("koala")

    assert app.execute() == 0


def test_execute_rejects_invalid_mode() -> None:
    app = mastodon_app.MastodonApp("bad-mode")

    assert app.execute() == 1

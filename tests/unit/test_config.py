import pytest
from pydantic import ValidationError

from src.config import Settings


def test_settings_loads_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "fake_token")
    settings = Settings()  # type: ignore[call-arg]
    assert settings.github_token == "fake_token"  # noqa: S105


def test_settings_fails_without_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    with pytest.raises(ValidationError):
        Settings()  # type: ignore[call-arg]

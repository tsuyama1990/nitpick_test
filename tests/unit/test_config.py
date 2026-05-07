from unittest.mock import patch

import pytest
from pydantic import ValidationError

from src.config.settings import Settings, get_settings


def test_settings_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "fake_token")
    settings = Settings()  # type: ignore[call-arg]
    assert settings.GITHUB_TOKEN == "fake_token"  # noqa: S105


def test_settings_missing_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    with pytest.raises(ValidationError):
        Settings()  # type: ignore[call-arg]


def test_settings_extra_forbid(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "fake_token")
    with pytest.raises(ValidationError):
        Settings(UNKNOWN_FIELD="test")  # type: ignore[call-arg]


@patch("src.config.settings._settings", None)
def test_get_settings_singleton(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "fake_token")
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2

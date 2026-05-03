import pytest
from pydantic import ValidationError

from src.config import Settings


def test_settings_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    test_token = "ghp_validtoken123"  # noqa: S105
    monkeypatch.setenv("GITHUB_TOKEN", test_token)
    settings = Settings()
    assert settings.github_token == test_token

def test_settings_missing_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    with pytest.raises(ValidationError):
        Settings()

def test_settings_empty_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "")
    with pytest.raises(ValidationError):
        Settings()

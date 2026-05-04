import pytest

from src.config import Settings, get_settings


def test_settings_loaded_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "test_token")
    settings = get_settings()
    assert settings.github_token == "test_token"  # noqa: S105


def test_settings_without_token() -> None:
    settings = Settings(github_token=None)
    assert settings.github_token is None

from pathlib import Path

import pytest
from pydantic import ValidationError

from src.config.settings import AppConfig, get_settings


@pytest.fixture(autouse=True)
def _reset_settings() -> None:
    """Reset the settings singleton before each test."""
    from src.config import settings
    settings._settings = None


def test_app_config_missing_github_token(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that missing GITHUB_TOKEN raises ValidationError."""
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    with pytest.raises(ValidationError):
        AppConfig(_env_file=None)  # type: ignore[call-arg]


def test_app_config_extra_forbidden() -> None:
    """Test that extra variables are forbidden."""
    with pytest.raises(ValidationError) as exc_info:
        AppConfig(
            GITHUB_TOKEN="dummy",  # noqa: S106
            UNKNOWN_VARIABLE="test",
            _env_file=None,  # type: ignore[call-arg]
        )
    assert any(err["type"] == "extra_forbidden" for err in exc_info.value.errors())


def test_app_config_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test successful instantiation with GITHUB_TOKEN."""
    monkeypatch.setenv("GITHUB_TOKEN", "dummy_token")
    config = AppConfig(_env_file=None)  # type: ignore[call-arg]
    assert config.GITHUB_TOKEN == "dummy_token"  # noqa: S105


def test_get_settings_singleton(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that get_settings returns the same instance."""
    monkeypatch.setenv("GITHUB_TOKEN", "dummy_token")
    settings_1 = get_settings()
    settings_2 = get_settings()
    assert settings_1 is settings_2


def test_app_config_from_env_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test loading from a specific .env file using tmp_path."""
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    env_file = tmp_path / ".env.test"
    env_file.write_text("GITHUB_TOKEN=file_token\n")

    config = AppConfig(_env_file=env_file)  # type: ignore[call-arg]
    assert config.GITHUB_TOKEN == "file_token"  # noqa: S105

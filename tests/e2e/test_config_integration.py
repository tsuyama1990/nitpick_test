from pathlib import Path

import pytest
from pydantic import ValidationError

from src.config.settings import AppConfig, get_settings


def test_get_settings_missing_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    # Clear the singleton for testing
    import src.config.settings as settings_module

    settings_module._settings = None

    with pytest.raises(ValidationError):
        get_settings()


def test_get_settings_valid_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "fake_token_123")
    # Clear the singleton for testing
    import src.config.settings as settings_module

    settings_module._settings = None

    settings = get_settings()
    assert settings.GITHUB_TOKEN == "fake_token_123"  # noqa: S105


def test_app_config_loads_from_env_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("GITHUB_TOKEN=secret_from_file\n")

    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    class TestConfig(AppConfig):
        model_config = AppConfig.model_config.copy()
        model_config["env_file"] = str(env_file)

    config = TestConfig(CACHE_TTL_SECONDS=3600, GITHUB_API_URL="https://api.github.com")  # type: ignore[call-arg]
    assert config.GITHUB_TOKEN == "secret_from_file"  # noqa: S105

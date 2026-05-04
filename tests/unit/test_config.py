import pytest
from pydantic import ValidationError

import src.config


def test_settings_default_values(monkeypatch: pytest.MonkeyPatch) -> None:
    # Ensure no environment variables interfere
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_API_BASE_URL", raising=False)
    monkeypatch.delenv("GITHUB_API_TIMEOUT", raising=False)

    settings = src.config.Settings()

    assert settings.GITHUB_TOKEN is None
    assert settings.GITHUB_API_BASE_URL == "https://api.github.com"
    assert settings.GITHUB_API_TIMEOUT == 10.0


def test_settings_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "fake_token")
    monkeypatch.setenv("GITHUB_API_BASE_URL", "https://api.fake.github.com")
    monkeypatch.setenv("GITHUB_API_TIMEOUT", "20.5")

    settings = src.config.Settings()

    assert settings.GITHUB_TOKEN == "fake_token"  # noqa: S105
    assert settings.GITHUB_API_BASE_URL == "https://api.fake.github.com"
    assert settings.GITHUB_API_TIMEOUT == 20.5


def test_settings_extra_forbid() -> None:
    # pydantic_settings extra_forbid applies to kwargs
    with pytest.raises(ValidationError):
        src.config.Settings(UNKNOWN_VARIABLE="should_fail")  # type: ignore[call-arg]


def test_get_settings_singleton(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    # Reset singleton state
    src.config._settings = None

    settings_1 = src.config.get_settings()
    settings_2 = src.config.get_settings()

    assert settings_1 is settings_2


def test_get_settings_singleton_initialization(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    src.config._settings = None

    settings = src.config.get_settings()
    assert isinstance(settings, src.config.Settings)

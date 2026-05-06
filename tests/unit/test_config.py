import os
from unittest.mock import patch

import pydantic
import pytest

from src.config import Settings, get_settings


def test_settings_loaded_from_env() -> None:
    with patch.dict(os.environ, {"GITHUB_TOKEN": "my_secret_token"}):
        settings = Settings()
        assert settings.GITHUB_TOKEN == "my_secret_token"  # noqa: S105


def test_settings_default_to_none() -> None:
    with patch.dict(os.environ, {}, clear=True):
        settings = Settings()
        assert settings.GITHUB_TOKEN is None


def test_settings_forbid_extra() -> None:
    with pytest.raises(pydantic.ValidationError) as exc_info:
        Settings(UNKNOWN_VARIABLE="test")  # type: ignore[call-arg]

    assert any(err["type"] == "extra_forbidden" for err in exc_info.value.errors())


def test_get_settings_singleton() -> None:
    with patch.dict(os.environ, {"GITHUB_TOKEN": "singleton_token"}):
        # we need to make sure _settings is reset for the test
        import src.config

        src.config._settings = None
        settings_1 = get_settings()
        settings_2 = get_settings()
        assert settings_1 is settings_2

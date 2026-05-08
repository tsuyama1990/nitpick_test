import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from src.domain_models.config import Settings, get_settings


def test_settings_valid() -> None:
    with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
        settings = Settings()  # type: ignore[call-arg]
        assert settings.GITHUB_TOKEN == "test_token"  # noqa: S105


def test_settings_missing_token() -> None:
    with patch.dict(os.environ, clear=True), pytest.raises(ValidationError):
        Settings()  # type: ignore[call-arg]


def test_settings_extra_forbid() -> None:
    with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}), pytest.raises(ValidationError):
        Settings(UNKNOWN_VARIABLE="test")  # type: ignore[call-arg]


@patch("src.domain_models.config._settings", None)
def test_get_settings_singleton() -> None:
    with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
        settings_1 = get_settings()
        settings_2 = get_settings()
        assert settings_1 is settings_2

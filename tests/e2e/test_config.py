import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from src.config import Settings, get_settings


@pytest.fixture(autouse=True)
def clear_settings_cache() -> None:
    """Clear the settings cache before each test."""
    get_settings.cache_clear()


@patch.dict(os.environ, {"GITHUB_TOKEN": "mocked_token"}, clear=True)
def test_settings_valid_token() -> None:
    """Test that Settings initializes correctly when GITHUB_TOKEN is present."""
    settings = get_settings()
    assert settings.GITHUB_TOKEN == "mocked_token"  # noqa: S105


@patch.dict(os.environ, {}, clear=True)
def test_settings_missing_token() -> None:
    """Test that Settings raises ValidationError when GITHUB_TOKEN is missing."""
    with pytest.raises(ValidationError) as exc_info:
        Settings()  # type: ignore[call-arg]

    assert "GITHUB_TOKEN" in str(exc_info.value)
    assert "Field required" in str(exc_info.value)


@patch.dict(os.environ, {"GITHUB_TOKEN": "mocked_token", "EXTRA_VAR": "unexpected"}, clear=True)
def test_settings_extra_forbid() -> None:
    """Test that Settings forbids extra environment variables if explicitly loaded."""
    # Settings loads only defined fields and extra='forbid' checks if extra fields are injected
    # However, env vars are generally loaded only for defined fields in base pydantic settings.
    # The 'extra=forbid' in SettingsConfigDict applies to kwargs passed explicitly or loaded manually
    # Let's ensure a kwarg raises ValidationError
    with pytest.raises(ValidationError) as exc_info:
        Settings(GITHUB_TOKEN="mocked_token", EXTRA_VAR="unexpected")  # type: ignore[call-arg] # noqa: S106

    assert "Extra inputs are not permitted" in str(exc_info.value)

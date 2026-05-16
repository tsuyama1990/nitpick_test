"""Unit tests for the application configuration."""

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from src.config import Settings, get_settings


def test_settings_initializes_with_token() -> None:
    """Test Settings initializes successfully when GITHUB_TOKEN is present."""
    with patch.dict(os.environ, {"GITHUB_TOKEN": "mock_token_123"}, clear=True):
        get_settings.cache_clear()
        settings = Settings()  # type: ignore[call-arg]
        assert settings.GITHUB_TOKEN == "mock_token_123"  # noqa: S105

        # also test singleton cache
        cached_settings = get_settings()
        assert cached_settings.GITHUB_TOKEN == "mock_token_123"  # noqa: S105


def test_settings_fails_without_token() -> None:
    """Test Settings raises ValidationError when GITHUB_TOKEN is missing."""
    with patch.dict(os.environ, {}, clear=True):
        get_settings.cache_clear()
        with pytest.raises(ValidationError, match="GITHUB_TOKEN"):
            Settings()  # type: ignore[call-arg]

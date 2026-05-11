import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from src.domain_models.config import Settings, get_settings


@pytest.fixture(autouse=True)
def _clear_cache() -> None:
    """Clear the lru_cache before each test to ensure fresh settings."""
    get_settings.cache_clear()


def test_settings_valid_token() -> None:
    """Test Settings initializes correctly with a valid token."""
    with patch.dict(os.environ, {"GITHUB_TOKEN": "dummy_token"}, clear=True):
        settings = Settings()  # type: ignore[call-arg]
        assert settings.GITHUB_TOKEN == "dummy_token"  # noqa: S105

        # Test the singleton accessor
        cached_settings = get_settings()
        assert cached_settings.GITHUB_TOKEN == "dummy_token"  # noqa: S105


def test_settings_missing_token() -> None:
    """Test Settings raises ValidationError when token is missing."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValidationError) as exc_info:
            Settings()  # type: ignore[call-arg]

        assert "GITHUB_TOKEN" in str(exc_info.value)

        with pytest.raises(ValidationError):
            get_settings()

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from src.domain_models.config import Settings, get_settings


@patch.dict(os.environ, {"GITHUB_TOKEN": "dummy_integration_token"}, clear=True)
def test_integration_settings_valid() -> None:
    """Integration test: Settings with valid environment variable."""
    get_settings.cache_clear()
    settings = get_settings()
    assert settings.GITHUB_TOKEN == "dummy_integration_token"  # noqa: S105


@patch.dict(os.environ, {}, clear=True)
def test_integration_settings_invalid_missing_token() -> None:
    """Integration test: Settings without required environment variable."""
    get_settings.cache_clear()
    with pytest.raises(ValidationError):
        Settings()  # type: ignore[call-arg]

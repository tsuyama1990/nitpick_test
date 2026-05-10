from unittest.mock import patch

import pytest
from pydantic import ValidationError

from src.config.settings import Settings, get_settings


def test_settings_initialization() -> None:
    """Test Settings requires GITHUB_TOKEN and forbids extra fields."""
    with patch.dict("os.environ", {"GITHUB_TOKEN": "test_token"}):
        settings = Settings()  # type: ignore[call-arg]
        assert settings.GITHUB_TOKEN == "test_token"  # noqa: S105


def test_settings_missing_token() -> None:
    """Test Settings fails if GITHUB_TOKEN is missing."""
    with patch.dict("os.environ", clear=True), pytest.raises(ValidationError):
        Settings()  # type: ignore[call-arg]


def test_settings_forbid_extra() -> None:
    """Test Settings forbids extra fields."""
    with patch.dict("os.environ", {"GITHUB_TOKEN": "test_token"}), pytest.raises(ValidationError):
        Settings(GITHUB_TOKEN="test_token", UNKNOWN_VAR="test")  # type: ignore[call-arg] # noqa: S106


def test_get_settings_singleton() -> None:
    """Test get_settings returns the same instance."""
    with patch.dict("os.environ", {"GITHUB_TOKEN": "test_token"}):
        settings_1 = get_settings()
        settings_2 = get_settings()
        assert settings_1 is settings_2

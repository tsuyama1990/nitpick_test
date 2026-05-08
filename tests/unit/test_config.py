from unittest.mock import patch

import pytest
from pydantic import ValidationError

from src.domain_models import config
from src.domain_models.config import Settings, get_settings


def test_settings_valid_token() -> None:
    with patch.dict("os.environ", {"GITHUB_TOKEN": "valid_token"}):
        settings = Settings()  # type: ignore[call-arg]
        assert settings.GITHUB_TOKEN == "valid_token"  # noqa: S105


def test_settings_missing_token() -> None:
    with patch.dict("os.environ", {}, clear=True), pytest.raises(ValidationError):
        Settings()  # type: ignore[call-arg]


def test_settings_extra_forbid() -> None:
    with patch.dict("os.environ", {"GITHUB_TOKEN": "token", "EXTRA_VAR": "extra"}):
        with pytest.raises(ValidationError) as exc:
            Settings(UNKNOWN_VARIABLE="test")  # type: ignore[call-arg]
        assert any(err["type"] == "extra_forbidden" for err in exc.value.errors())


def test_get_settings_singleton() -> None:
    with patch.dict("os.environ", {"GITHUB_TOKEN": "singleton_token"}):
        config._settings = None
        settings_1 = get_settings()
        settings_2 = get_settings()
        assert settings_1 is settings_2
        assert settings_1.GITHUB_TOKEN == "singleton_token"  # noqa: S105

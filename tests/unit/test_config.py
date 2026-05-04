import pytest

import src.config
from src.config import Settings, get_settings


def test_settings_forbid_extra() -> None:
    with pytest.raises(ValueError, match="Extra inputs are not permitted"):
        # Mypy will complain, but we need to verify Pydantic behavior
        Settings(github_token="dummy", UNKNOWN_VARIABLE="test")  # type: ignore[call-arg]


def test_get_settings_singleton() -> None:
    # Reset singleton state
    src.config._settings = None
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2

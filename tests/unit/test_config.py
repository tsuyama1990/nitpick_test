from typing import Any

import pytest

from src.config import Settings


def test_settings_forbidden() -> None:
    kwargs: dict[str, Any] = {"GITHUB_TOKEN": "abc", "UNKNOWN_VAR": "test"}
    with pytest.raises(ValueError, match="Extra forbidden field"):
        Settings(**kwargs)

import os
from unittest.mock import patch

import pytest

from src.config import get_github_token


def test_get_github_token_success() -> None:
    with patch.dict(os.environ, {"GITHUB_TOKEN": "valid_token"}):
        token = get_github_token()
        assert token == "valid_token"

def test_get_github_token_missing() -> None:
    with patch.dict(os.environ, {}, clear=True), pytest.raises(ValueError):
        get_github_token()

def test_get_github_token_empty() -> None:
    with patch.dict(os.environ, {"GITHUB_TOKEN": "   "}), pytest.raises(ValueError):
        get_github_token()

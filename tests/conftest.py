import os
from collections.abc import Generator
from unittest.mock import patch

import pytest

from src.domain_models.config import get_settings


@pytest.fixture(autouse=True)
def _reset_cache() -> Generator[None, None, None]:
    """Reset the settings cache before each test to ensure isolation."""
    get_settings.cache_clear()

    # Also mock environment variables to prevent accidental live usage
    with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}, clear=True):
        yield

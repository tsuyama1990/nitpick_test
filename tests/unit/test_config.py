import os
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from src.config import get_cache_config
from src.domain_models.config import CacheConfig


def test_cache_config_default_values() -> None:
    with patch.dict(os.environ, {}, clear=True):
        config = CacheConfig()
        assert config.cache_dir == Path(".cache")
        assert config.cache_ttl_seconds == 3600


def test_cache_config_custom_values() -> None:
    with patch.dict(
        os.environ,
        {"CACHE_DIR": "/custom/path/custom_cache", "CACHE_TTL_SECONDS": "7200"},
        clear=True,
    ):
        config = CacheConfig()
        assert config.cache_dir == Path("/custom/path/custom_cache")
        assert config.cache_ttl_seconds == 7200


def test_cache_config_invalid_ttl() -> None:
    with (
        patch.dict(os.environ, {"CACHE_TTL_SECONDS": "not_an_int"}, clear=True),
        pytest.raises(ValidationError),
    ):
        CacheConfig()


def test_get_cache_config_singleton() -> None:
    with patch.dict(os.environ, {}, clear=True):
        get_cache_config.cache_clear()
        config1 = get_cache_config()
        config2 = get_cache_config()
        assert config1 is config2

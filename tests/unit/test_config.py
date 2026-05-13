import os
from unittest import mock

import pytest
from pydantic import ValidationError

from src.domain_models.config import CacheConfig


def test_cache_config_defaults() -> None:
    """Test CacheConfig loads default values correctly."""
    with mock.patch.dict(os.environ, {}, clear=True):
        config = CacheConfig()
        assert config.CACHE_DIR == ".cache"
        assert config.CACHE_TTL_SECONDS == 3600


def test_cache_config_overrides() -> None:
    """Test CacheConfig loads overridden environment variables correctly."""
    with mock.patch.dict(
        os.environ,
        {"CACHE_DIR": "/custom/cache_dir", "CACHE_TTL_SECONDS": "7200"},
        clear=True
    ):
        config = CacheConfig()
        assert config.CACHE_DIR == "/custom/cache_dir"
        assert config.CACHE_TTL_SECONDS == 7200


def test_cache_config_extra_forbid() -> None:
    """Test CacheConfig raises ValidationError if extra variables are passed."""
    with mock.patch.dict(os.environ, {"EXTRA_VAR": "should_fail"}, clear=True), pytest.raises(ValidationError):
            CacheConfig(EXTRA_VAR="should_fail") # type: ignore[call-arg]

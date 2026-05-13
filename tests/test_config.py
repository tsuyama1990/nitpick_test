import os
from unittest.mock import patch

from src.domain_models.config import CacheConfig


def test_cache_config_defaults() -> None:
    with patch.dict(os.environ, {}, clear=True):
        config = CacheConfig()
        assert config.cache_dir == ".cache"
        assert config.cache_ttl_seconds == 3600

def test_cache_config_overrides() -> None:
    with patch.dict(os.environ, {"CACHE_DIR": "/custom/path", "CACHE_TTL_SECONDS": "7200"}, clear=True):
        config = CacheConfig()
        assert config.cache_dir == "/custom/path"
        assert config.cache_ttl_seconds == 7200

import os
from unittest import mock

from src.config import get_settings


def test_config_loading() -> None:
    get_settings.cache_clear()
    with mock.patch.dict(os.environ, {"CACHE_DIR": ".custom_cache", "TTL_SECONDS": "7200"}):
        settings = get_settings()
        assert settings.cache_dir == ".custom_cache"
        assert settings.ttl_seconds == 7200

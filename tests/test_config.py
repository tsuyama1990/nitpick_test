import os
from unittest import mock

from src.config import get_settings
from src.domain_models.config import AppSettings

def test_config_defaults() -> None:
    settings = AppSettings()
    assert settings.cache_dir.name == ".cache"

def test_config_env_override() -> None:
    with mock.patch.dict(os.environ, {"CACHE_DIR": "/tmp/custom_cache"}, clear=True):
        settings = AppSettings()
        assert str(settings.cache_dir) == "/tmp/custom_cache"

def test_get_settings_caching() -> None:
    get_settings.cache_clear()
    settings_1 = get_settings()
    settings_2 = get_settings()
    assert settings_1 is settings_2

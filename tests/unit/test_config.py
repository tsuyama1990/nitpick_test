import os
from pathlib import Path
from src.config import get_settings
from src.domain_models.config import AppConfig
import pytest

@pytest.fixture(autouse=True)
def _clear_cache() -> None:
    get_settings.cache_clear()

def test_app_config_default_cache_dir() -> None:
    config = AppConfig()
    assert config.cache_dir == Path(".cache")

def test_get_settings_caching() -> None:
    settings_1 = get_settings()
    settings_2 = get_settings()
    assert settings_1 is settings_2

def test_app_config_custom_cache_dir(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CACHE_DIR", "/custom/cache/dir")
    config = AppConfig()
    assert config.cache_dir == Path("/custom/cache/dir")

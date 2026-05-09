import time
from pathlib import Path
from unittest.mock import patch

import polars as pl
import pytest

from src.storage.cache_manager import CacheManager


@pytest.fixture
def cache_dir(tmp_path: Path) -> Path:
    return tmp_path / "app_name"


@pytest.fixture
def cache_manager(cache_dir: Path) -> CacheManager:
    with (
        patch("os.getenv", return_value=str(cache_dir)),
        patch("src.storage.cache_manager.get_settings") as mock_get_settings,
    ):
        mock_get_settings.return_value.CACHE_DIR_NAME = "app_name"
        return CacheManager(ttl_seconds=60)


def test_cache_manager_save_and_load(cache_manager: CacheManager) -> None:
    df = pl.DataFrame({"a": [1, 2], "b": [3, 4]})
    key = "test_key"

    # Save the dataframe
    cache_manager.save(key, df)

    # Ensure it exists on disk
    assert cache_manager._get_cache_path(key).exists()

    # Load it back
    loaded_df = cache_manager.load(key)
    assert loaded_df is not None
    assert loaded_df.equals(df)


def test_cache_manager_load_nonexistent(cache_manager: CacheManager) -> None:
    assert cache_manager.load("non_existent_key") is None


def test_cache_manager_ttl_expired(cache_manager: CacheManager) -> None:
    df = pl.DataFrame({"a": [1]})
    key = "expired_key"

    cache_manager.save(key, df)

    # This test is just a placeholder because we use time.time() patch below.


def test_cache_manager_ttl_expired_time_mock(cache_manager: CacheManager) -> None:
    df = pl.DataFrame({"a": [1]})
    key = "expired_key_time"

    cache_manager.save(key, df)
    path = cache_manager._get_cache_path(key)

    with patch("time.time", return_value=time.time() + 100):
        loaded = cache_manager.load(key)
        assert loaded is None
        assert not path.exists()

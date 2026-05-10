import pathlib
import time
from unittest.mock import patch

import polars as pl
import pytest

from src.storage.cache import CacheManager


@pytest.fixture
def temp_cache_dir(tmp_path: pathlib.Path) -> pathlib.Path:
    return tmp_path / "cache"


def test_cache_manager_initialization(temp_cache_dir: pathlib.Path) -> None:
    with patch.dict("os.environ", {"CACHE_DIR": str(temp_cache_dir)}):
        manager = CacheManager(ttl_seconds=100)
        assert manager.cache_dir == temp_cache_dir
        assert manager.ttl_seconds == 100
        assert manager.cache_dir.exists()


def test_cache_save_and_load(temp_cache_dir: pathlib.Path) -> None:
    with patch.dict("os.environ", {"CACHE_DIR": str(temp_cache_dir)}):
        manager = CacheManager()
        df = pl.DataFrame({"a": [1, 2, 3]})

        manager.save(df, "test-owner", "test-repo", "commits")

        loaded_df = manager.load("test-owner", "test-repo", "commits")
        assert loaded_df is not None
        assert loaded_df.equals(df)


def test_cache_miss(temp_cache_dir: pathlib.Path) -> None:
    with patch.dict("os.environ", {"CACHE_DIR": str(temp_cache_dir)}):
        manager = CacheManager()
        loaded_df = manager.load("test-owner", "test-repo", "nonexistent")
        assert loaded_df is None


def test_cache_ttl_expiration(temp_cache_dir: pathlib.Path) -> None:
    with patch.dict("os.environ", {"CACHE_DIR": str(temp_cache_dir)}):
        manager = CacheManager(ttl_seconds=1)  # Very short TTL
        df = pl.DataFrame({"a": [1, 2, 3]})

        manager.save(df, "test-owner", "test-repo", "commits")

        # Simulate time passing by patching file modification time
        with patch.object(pathlib.Path, "stat") as mock_stat:
            # Set mtime to 10 seconds ago
            mock_stat.return_value.st_mtime = time.time() - 10
            loaded_df = manager.load("test-owner", "test-repo", "commits")
            assert loaded_df is None

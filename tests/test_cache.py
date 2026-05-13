import os
import pathlib

import polars as pl
import pytest

from src.processing.cache import LocalCache


@pytest.fixture
def dummy_df() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "date": ["2023-01-01", "2023-01-02"],
            "commits": [10, 20],
        }
    )


def test_cache_initialization(tmp_path: pathlib.Path) -> None:
    cache_dir = tmp_path / "nested" / "dir"
    cache = LocalCache(cache_dir=cache_dir)
    assert cache.cache_dir == cache_dir
    assert cache_dir.exists()
    assert cache_dir.is_dir()


def test_cache_hit_workflow(tmp_path: pathlib.Path, dummy_df: pl.DataFrame) -> None:
    cache = LocalCache(cache_dir=tmp_path)
    cache.set_value("test_key", dummy_df)

    cached_df = cache.get("test_key")
    assert cached_df is not None
    assert isinstance(cached_df, pl.DataFrame)
    assert cached_df.equals(dummy_df)


def test_cache_miss_file_not_found(tmp_path: pathlib.Path) -> None:
    cache = LocalCache(cache_dir=tmp_path)
    cached_df = cache.get("non_existent_key")
    assert cached_df is None


def test_cache_expiration_ttl_check(tmp_path: pathlib.Path, dummy_df: pl.DataFrame) -> None:
    cache = LocalCache(cache_dir=tmp_path, ttl_seconds=3600)
    cache.set_value("test_key", dummy_df)

    # Path where the cache writes the file
    file_path = tmp_path / "test_key.parquet"
    assert file_path.exists()

    # Backdate the modification time to be older than TTL (e.g., 2 hours ago)
    now = pathlib.Path.stat(file_path).st_mtime
    past_time = now - 7200
    os.utime(file_path, (now, past_time))

    # Test retrieving after TTL has expired
    cached_df = cache.get("test_key")
    assert cached_df is None

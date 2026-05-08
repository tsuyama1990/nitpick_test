import os
import pathlib
import time

import polars as pl
import pytest

from src.cache import ParquetCache


@pytest.fixture
def cache(tmp_path: pathlib.Path) -> ParquetCache:
    # Use monkeypatch to set CACHE_DIR to a temporary directory
    os.environ["CACHE_DIR"] = str(tmp_path)
    # also set other settings for the test
    os.environ["GITHUB_TOKEN"] = "dummy"  # noqa: S105
    return ParquetCache(ttl_seconds=1)


def test_cache_save_and_load(cache: ParquetCache) -> None:
    df = pl.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    key = "test_repo/data"
    cache.save(key, df)

    assert cache.is_valid(key) is True
    loaded_df = cache.load(key)
    assert loaded_df is not None
    assert loaded_df.equals(df)


def test_cache_expiration(cache: ParquetCache) -> None:
    df = pl.DataFrame({"a": [1]})
    key = "test_ttl"
    cache.save(key, df)

    assert cache.is_valid(key) is True

    time.sleep(1.1)

    assert cache.is_valid(key) is False
    assert cache.load(key) is None


def test_cache_missing_key(cache: ParquetCache) -> None:
    assert cache.is_valid("missing") is False
    assert cache.load("missing") is None


def test_cache_clear(cache: ParquetCache) -> None:
    df = pl.DataFrame({"a": [1]})
    key = "test_clear"
    cache.save(key, df)
    assert cache.is_valid(key) is True

    cache.clear(key)
    assert cache.is_valid(key) is False

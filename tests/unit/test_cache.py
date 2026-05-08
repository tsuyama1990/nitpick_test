import os
import pathlib
import time

import polars as pl
import pytest

from src.cache import ParquetCache


@pytest.fixture
def cache(tmp_path: pathlib.Path) -> ParquetCache:
    os.environ["CACHE_DIR"] = str(tmp_path)
    return ParquetCache(ttl_seconds=1)


def test_cache_save_and_load(cache: ParquetCache) -> None:
    df = pl.DataFrame({"a": [1, 2]})
    cache.save("key1", df)
    assert cache.is_valid("key1") is True
    assert cache.load("key1").equals(df)  # type: ignore


def test_cache_expiration(cache: ParquetCache) -> None:
    cache.save("key_ttl", pl.DataFrame({"a": [1]}))
    time.sleep(1.1)
    assert cache.is_valid("key_ttl") is False


def test_cache_missing_key(cache: ParquetCache) -> None:
    assert cache.is_valid("miss") is False
    assert cache.load("miss") is None


def test_cache_clear(cache: ParquetCache) -> None:
    cache.save("clear", pl.DataFrame({"a": [1]}))
    cache.clear("clear")
    assert cache.is_valid("clear") is False

import pathlib
import time
from typing import Any

import polars as pl
import pytest

from src.storage.cache import CacheStorage


def test_cache_storage(tmp_path: pathlib.Path) -> None:
    cache = CacheStorage(cache_dir=str(tmp_path), ttl_seconds=10)
    df = pl.DataFrame({"a": [1, 2, 3]})

    # Cache miss
    assert cache.get("test_key") is None

    # Cache set and hit
    cache.set("test_key", df)
    cached_df = cache.get("test_key")
    assert cached_df is not None
    assert cached_df.equals(df)


def test_cache_expiry(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cache = CacheStorage(cache_dir=str(tmp_path), ttl_seconds=1)
    df = pl.DataFrame({"a": [1]})
    cache.set("test_key", df)

    # Mock time.time to be 2 seconds in the future
    current_time = time.time()
    monkeypatch.setattr(time, "time", lambda: current_time + 2.0)

    assert cache.get("test_key") is None


class MockCacheError(Exception):
    pass


def test_cache_read_error(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cache = CacheStorage(cache_dir=str(tmp_path))
    df = pl.DataFrame({"a": [1]})
    cache.set("test_key", df)

    def mock_read_parquet(*args: Any, **kwargs: Any) -> None:
        err_msg = "Mock read error"
        raise MockCacheError(err_msg)

    monkeypatch.setattr(pl, "read_parquet", mock_read_parquet)
    assert cache.get("test_key") is None


def test_cache_write_error(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cache = CacheStorage(cache_dir=str(tmp_path))
    df = pl.DataFrame({"a": [1]})

    def mock_write_parquet(*args: Any, **kwargs: Any) -> None:
        err_msg = "Mock write error"
        raise MockCacheError(err_msg)

    monkeypatch.setattr(pl.DataFrame, "write_parquet", mock_write_parquet)
    # Shouldn't raise an exception
    cache.set("test_key", df)

import os
import time
from pathlib import Path

import polars as pl
import pytest

from processing.cache import LocalCache


def test_directory_creation(tmp_path: Path) -> None:
    nested_dir = tmp_path / "nested" / "dir"
    LocalCache(cache_dir=nested_dir)
    assert nested_dir.exists()
    assert nested_dir.is_dir()


def test_cache_hit(tmp_path: Path) -> None:
    cache = LocalCache(cache_dir=tmp_path)
    df = pl.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    cache.set("test_key", df)

    retrieved_df = cache.get("test_key")
    assert retrieved_df is not None
    assert isinstance(retrieved_df, pl.DataFrame)
    assert retrieved_df.equals(df)


def test_cache_miss(tmp_path: Path) -> None:
    cache = LocalCache(cache_dir=tmp_path)
    assert cache.get("non_existent_key") is None


def test_cache_expiration(tmp_path: Path) -> None:
    ttl_seconds = 3600
    cache = LocalCache(cache_dir=tmp_path, ttl_seconds=ttl_seconds)
    df = pl.DataFrame({"a": [1]})
    cache.set("test_key", df)

    target_file = tmp_path / "test_key.parquet"

    # Artificially backdate the file modification timestamp past the TTL
    past_time = time.time() - ttl_seconds - 100
    os.utime(target_file, (past_time, past_time))

    assert cache.get("test_key") is None




def test_cache_default_config_initialization(monkeypatch: pytest.MonkeyPatch) -> None:
    # Ensure environment is clean
    monkeypatch.delenv("CACHE_DIR", raising=False)
    cache = LocalCache()
    assert str(cache.cache_dir) == ".cache"

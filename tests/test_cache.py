import os
import time
from pathlib import Path

import polars as pl

from src.processing.cache import LocalCache


def test_cache_directory_creation(tmp_path: Path) -> None:
    cache_dir = tmp_path / "nested" / "dir"
    cache = LocalCache(cache_dir=cache_dir)
    assert cache_dir.exists()
    assert cache_dir.is_dir()
    assert cache.cache_dir == cache_dir


def test_cache_hit_workflow(tmp_path: Path) -> None:
    cache_dir = tmp_path / "cache"
    cache = LocalCache(cache_dir=cache_dir)

    df = pl.DataFrame({"date": ["2024-01-01", "2024-01-02"], "commits": [10, 20]})

    cache.set("test_key", df)

    retrieved_df = cache.get("test_key")
    assert retrieved_df is not None
    assert isinstance(retrieved_df, pl.DataFrame)
    assert retrieved_df.equals(df)


def test_cache_miss_file_not_found(tmp_path: Path) -> None:
    cache_dir = tmp_path / "cache"
    cache = LocalCache(cache_dir=cache_dir)

    retrieved_df = cache.get("non_existent_key")
    assert retrieved_df is None


def test_cache_expiration_ttl_check(tmp_path: Path) -> None:
    cache_dir = tmp_path / "cache"
    cache = LocalCache(cache_dir=cache_dir, ttl_seconds=3600)

    df = pl.DataFrame({"data": [1, 2, 3]})
    cache.set("test_key", df)

    file_path = cache_dir / "test_key.parquet"
    assert file_path.exists()

    # Artificially backdate file modified time to be older than TTL
    # ttl is 3600, make it 4000 seconds older than current time
    current_time = time.time()
    past_time = current_time - 4000
    os.utime(file_path, (past_time, past_time))

    retrieved_df = cache.get("test_key")
    assert retrieved_df is None

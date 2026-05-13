import os
import time
from pathlib import Path

import polars as pl

from src.processing.cache import LocalCache


def test_cache_initialization_creates_directory(tmp_path: Path) -> None:
    cache_dir = tmp_path / "nested" / "dir"
    assert not cache_dir.exists()

    LocalCache(cache_dir=cache_dir)
    assert cache_dir.exists()
    assert cache_dir.is_dir()


def test_cache_hit_workflow(tmp_path: Path) -> None:
    cache = LocalCache(cache_dir=tmp_path)

    df = pl.DataFrame({"date": ["2024-01-01", "2024-01-02"], "commits": [10, 20]})

    key = "test_key"
    cache.set(key, df)

    retrieved_df = cache.get(key)

    assert retrieved_df is not None
    assert isinstance(retrieved_df, pl.DataFrame)
    assert df.equals(retrieved_df)


def test_cache_miss_file_not_found(tmp_path: Path) -> None:
    cache = LocalCache(cache_dir=tmp_path)
    retrieved_df = cache.get("non_existent_key")
    assert retrieved_df is None


def test_cache_expiration_ttl_check(tmp_path: Path) -> None:
    cache = LocalCache(cache_dir=tmp_path, ttl_seconds=3600)

    df = pl.DataFrame({"data": [1, 2, 3]})
    key = "test_expire"
    cache.set(key, df)

    # Backdate the file's modification time
    file_path = tmp_path / f"{key}.parquet"
    assert file_path.exists()

    # Set the modification time to 2 hours ago (7200 seconds)
    current_time = time.time()
    past_time = current_time - 7200
    os.utime(file_path, (current_time, past_time))

    retrieved_df = cache.get(key)
    assert retrieved_df is None

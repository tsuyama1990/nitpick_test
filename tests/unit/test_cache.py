import os
import time
from pathlib import Path

import polars as pl

from src.processing.cache import LocalCache


def test_directory_creation(tmp_path: Path) -> None:
    """Verify that initializing LocalCache correctly creates nested directories."""
    nested_dir = tmp_path / "nested" / "dir"
    LocalCache(cache_dir=nested_dir, ttl_seconds=3600)
    assert nested_dir.exists()
    assert nested_dir.is_dir()


def test_cache_hit_workflow(tmp_path: Path) -> None:
    """Verify saving and retrieving a Polars DataFrame successfully without data loss."""
    cache = LocalCache(cache_dir=tmp_path, ttl_seconds=3600)

    df = pl.DataFrame(
        {
            "col_a": [1, 2, 3],
            "col_b": ["a", "b", "c"],
        }
    )

    cache.set("test_key", df)

    retrieved_df = cache.get("test_key")

    assert retrieved_df is not None
    assert isinstance(retrieved_df, pl.DataFrame)
    assert retrieved_df.equals(df)


def test_cache_miss_file_not_found(tmp_path: Path) -> None:
    """Verify retrieving a non-existent key returns None."""
    cache = LocalCache(cache_dir=tmp_path, ttl_seconds=3600)

    retrieved_df = cache.get("non_existent_key")
    assert retrieved_df is None


def test_cache_expiration_ttl_check(tmp_path: Path) -> None:
    """Verify setting a file's st_mtime to the past correctly invalidates the cache and returns None."""
    cache = LocalCache(cache_dir=tmp_path, ttl_seconds=3600)

    df = pl.DataFrame(
        {
            "col_a": [1, 2, 3],
        }
    )

    cache.set("test_key", df)

    # Backdate the file's modification timestamp by 2 hours
    file_path = tmp_path / "test_key.parquet"
    past_time = time.time() - 7200
    os.utime(file_path, (past_time, past_time))

    retrieved_df = cache.get("test_key")
    assert retrieved_df is None

import os
import time
from pathlib import Path

import polars as pl
from polars.testing import assert_frame_equal

from src.config import get_settings
from src.processing.cache import LocalCache


def test_cache_directory_creation(tmp_path: Path) -> None:
    cache_dir = tmp_path / "nested" / "dir"
    LocalCache(cache_dir=cache_dir)
    assert cache_dir.exists()
    assert cache_dir.is_dir()


def test_cache_hit_workflow(tmp_path: Path) -> None:
    cache_dir = tmp_path / get_settings().default_cache_subdir
    cache = LocalCache(cache_dir=cache_dir)
    df = pl.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    cache.set("test_key", df)
    retrieved_df = cache.get("test_key")

    assert retrieved_df is not None
    assert_frame_equal(retrieved_df, df)


def test_cache_miss_workflow(tmp_path: Path) -> None:
    cache_dir = tmp_path / get_settings().default_cache_subdir
    cache = LocalCache(cache_dir=cache_dir)
    retrieved_df = cache.get("non_existent_key")

    assert retrieved_df is None


def test_cache_expiration_ttl_check(tmp_path: Path) -> None:
    cache_dir = tmp_path / get_settings().default_cache_subdir
    # Setting TTL to 100 seconds
    cache = LocalCache(cache_dir=cache_dir, ttl_seconds=100)
    df = pl.DataFrame({"a": [1, 2, 3]})
    cache.set("test_key", df)

    # Artificially backdate the file modification timestamp so it appears older than TTL
    file_path = cache_dir / "test_key.parquet"
    past_time = time.time() - 200
    os.utime(file_path, (past_time, past_time))

    retrieved_df = cache.get("test_key")
    assert retrieved_df is None

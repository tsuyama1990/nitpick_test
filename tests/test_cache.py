import os
import time
from pathlib import Path

import polars as pl
from src.processing.cache import LocalCache


def test_local_cache_directory_creation(tmp_path: Path) -> None:
    nested_path = tmp_path / "nested" / "dir"
    LocalCache(cache_dir=nested_path, ttl_seconds=3600)
    assert nested_path.exists()
    assert nested_path.is_dir()


def test_local_cache_hit_workflow(tmp_path: Path) -> None:
    cache = LocalCache(cache_dir=tmp_path, ttl_seconds=3600)
    df = pl.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    cache.set("test_key", df)

    retrieved_df = cache.get("test_key")
    assert retrieved_df is not None
    assert isinstance(retrieved_df, pl.DataFrame)
    assert df.equals(retrieved_df)
    assert df.schema == retrieved_df.schema


def test_local_cache_miss_file_not_found(tmp_path: Path) -> None:
    cache = LocalCache(cache_dir=tmp_path, ttl_seconds=3600)
    retrieved_df = cache.get("non_existent_key")
    assert retrieved_df is None


def test_local_cache_expiration_ttl_check(tmp_path: Path) -> None:
    cache = LocalCache(cache_dir=tmp_path, ttl_seconds=3600)
    df = pl.DataFrame({"a": [1, 2, 3]})
    cache.set("test_key", df)

    # Backdate the file's modification time to make it older than TTL
    file_path = tmp_path / "test_key.parquet"
    old_time = time.time() - 4000
    os.utime(file_path, (old_time, old_time))

    retrieved_df = cache.get("test_key")
    assert retrieved_df is None

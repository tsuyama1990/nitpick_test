import os
import time
from pathlib import Path

import polars as pl

from src.processing.cache import LocalCache


def test_directory_creation(tmp_path: Path) -> None:
    cache_dir = tmp_path / "nested" / "dir"
    LocalCache(cache_dir=cache_dir)
    assert cache_dir.exists()
    assert cache_dir.is_dir()


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
    cache = LocalCache(cache_dir=tmp_path, ttl_seconds=3600)
    df = pl.DataFrame({"a": [1]})
    cache.set("test_key", df)

    file_path = tmp_path / "test_key.parquet"
    assert file_path.exists()

    # Backdate the file's modification time by 2 hours
    past_time = time.time() - 7200
    os.utime(file_path, (past_time, past_time))

    retrieved_df = cache.get("test_key")
    assert retrieved_df is None

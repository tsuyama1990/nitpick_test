import os
import time
import polars as pl
from pathlib import Path
from src.processing.cache import LocalCache

def test_local_cache_directory_creation(tmp_path: Path) -> None:
    nested_path = tmp_path / "nested" / "dir"
    LocalCache(cache_dir=nested_path)
    assert nested_path.exists()
    assert nested_path.is_dir()

def test_local_cache_hit_workflow(tmp_path: Path) -> None:
    cache = LocalCache(cache_dir=tmp_path)
    df = pl.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    cache.set("test_key", df)

    retrieved_df = cache.get("test_key")
    assert retrieved_df is not None
    assert isinstance(retrieved_df, pl.DataFrame)
    assert retrieved_df.equals(df)

def test_local_cache_miss(tmp_path: Path) -> None:
    cache = LocalCache(cache_dir=tmp_path)
    retrieved_df = cache.get("non_existent_key")
    assert retrieved_df is None

def test_local_cache_expiration(tmp_path: Path) -> None:
    ttl = 3600
    cache = LocalCache(cache_dir=tmp_path, ttl_seconds=ttl)
    df = pl.DataFrame({"a": [1]})
    cache.set("test_key", df)

    path = tmp_path / "test_key.parquet"

    # Backdate the file's modification timestamp
    old_time = time.time() - (ttl + 10)
    os.utime(path, (old_time, old_time))

    retrieved_df = cache.get("test_key")
    assert retrieved_df is None

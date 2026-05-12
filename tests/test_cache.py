import os
import time
from pathlib import Path

import polars as pl

from src.processing.cache import LocalCache


def test_directory_creation(tmp_path: Path) -> None:
    """Verify directory structure is created upon initialization."""
    nested_path = tmp_path / "nested" / "dir"
    LocalCache(cache_dir=nested_path)
    assert nested_path.exists()
    assert nested_path.is_dir()


def test_cache_hit_workflow(tmp_path: Path) -> None:
    """Verify saving and immediately retrieving a DataFrame."""
    cache = LocalCache(cache_dir=tmp_path)
    df = pl.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})

    cache.set("test_key", df)
    retrieved_df = cache.get("test_key")

    assert retrieved_df is not None
    assert isinstance(retrieved_df, pl.DataFrame)
    assert retrieved_df.equals(df)


def test_cache_miss_file_not_found(tmp_path: Path) -> None:
    """Verify retrieval returns None for a non-existent file."""
    cache = LocalCache(cache_dir=tmp_path)
    assert cache.get("non_existent_key") is None


def test_cache_expiration_ttl_check(tmp_path: Path) -> None:
    """Verify retrieval returns None for an expired file based on TTL."""
    from src.config import get_settings

    settings = get_settings()
    ttl = settings.cache_ttl
    cache = LocalCache(cache_dir=tmp_path, ttl_seconds=ttl)
    df = pl.DataFrame({"a": [1]})

    cache.set("test_key", df)

    # Backdate the file's modification time to simulate expiration
    file_path = tmp_path / "test_key.parquet"
    assert file_path.exists()

    # Calculate a time older than the TTL
    expired_time = time.time() - (ttl + 10)

    # Use os.utime to set access and modification times
    os.utime(file_path, (expired_time, expired_time))

    # The file should now be considered expired
    assert cache.get("test_key") is None

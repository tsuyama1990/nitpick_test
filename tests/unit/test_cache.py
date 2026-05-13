import os
import time
from pathlib import Path

import polars as pl
import pytest
from src.processing.cache import LocalCache


@pytest.fixture
def dummy_df() -> pl.DataFrame:
    """Fixture providing a dummy Polars DataFrame."""
    return pl.DataFrame({
        "date": ["2024-01-01", "2024-01-02"],
        "commits": [10, 15]
    })


def test_local_cache_initialization_creates_directory(tmp_path: Path) -> None:
    """Test that LocalCache creates the nested directory structure if it doesn't exist."""
    nested_dir = tmp_path / "nested" / "dir"
    LocalCache(cache_dir=nested_dir, ttl_seconds=3600)
    assert nested_dir.exists()
    assert nested_dir.is_dir()


def test_local_cache_hit_workflow(tmp_path: Path, dummy_df: pl.DataFrame) -> None:
    """Test saving a DataFrame and immediately retrieving it (cache hit)."""
    cache = LocalCache(cache_dir=tmp_path, ttl_seconds=3600)

    # Set the data
    cache.set("test_key", dummy_df)

    # Get the data
    retrieved_df = cache.get("test_key")

    assert retrieved_df is not None
    assert isinstance(retrieved_df, pl.DataFrame)
    assert retrieved_df.equals(dummy_df)


def test_local_cache_miss_file_not_found(tmp_path: Path) -> None:
    """Test that getting a non-existent key returns None."""
    cache = LocalCache(cache_dir=tmp_path, ttl_seconds=3600)

    retrieved_df = cache.get("non_existent_key")
    assert retrieved_df is None


def test_local_cache_expiration_ttl_check(tmp_path: Path, dummy_df: pl.DataFrame) -> None:
    """Test that retrieving an expired cache file returns None."""
    ttl_seconds = 3600
    cache = LocalCache(cache_dir=tmp_path, ttl_seconds=ttl_seconds)

    cache.set("test_key", dummy_df)

    file_path = tmp_path / "test_key.parquet"
    assert file_path.exists()

    # Manipulate file metadata to simulate expiration (backdate by TTL + 10 seconds)
    current_time = time.time()
    past_time = current_time - (ttl_seconds + 10)
    os.utime(file_path, (past_time, past_time))

    # Retrieve should now return None
    retrieved_df = cache.get("test_key")
    assert retrieved_df is None

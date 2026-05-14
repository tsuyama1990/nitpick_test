import os
import time
from pathlib import Path

import polars as pl
import pytest

from src.processing.cache import LocalCache


def test_directory_creation(tmp_path: Path) -> None:
    # Use nested path inside tmp_path to test `parents=True`
    nested_path = tmp_path / "nested" / "dir"

    # Initialize LocalCache
    LocalCache(nested_path)

    # Assert directory creation
    assert nested_path.exists()
    assert nested_path.is_dir()


def test_cache_hit(tmp_path: Path) -> None:
    # Arrange
    cache = LocalCache(tmp_path)
    df = pl.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    key = "test_key"

    # Act
    cache.set(key, df)
    retrieved_df = cache.get(key)

    # Assert
    assert retrieved_df is not None
    assert isinstance(retrieved_df, pl.DataFrame)
    assert retrieved_df.equals(df)


def test_cache_miss(tmp_path: Path) -> None:
    # Arrange
    cache = LocalCache(tmp_path)

    # Act
    retrieved_df = cache.get("non_existent_key")

    # Assert
    assert retrieved_df is None


def test_cache_expiration(tmp_path: Path) -> None:
    # Arrange
    ttl_seconds = 10
    cache = LocalCache(tmp_path, ttl_seconds=ttl_seconds)
    df = pl.DataFrame({"a": [1, 2, 3]})
    key = "test_expire_key"

    # Act
    cache.set(key, df)

    # Assert it exists right after creation
    assert cache.get(key) is not None

    # Backdate the file's modification timestamp to trigger expiration
    file_path = cache._get_file_path(key)
    past_time = time.time() - (ttl_seconds + 5)
    os.utime(file_path, (past_time, past_time))

    # Try retrieving it again
    retrieved_df = cache.get(key)

    # Assert it returns None due to expiration
    assert retrieved_df is None


def test_cache_settings(monkeypatch: "pytest.MonkeyPatch") -> None:
    from src.processing.cache import LocalCache

    monkeypatch.setenv("CACHE_DIR", ".custom_cache")
    cache = LocalCache()
    assert str(cache.cache_dir) == ".custom_cache"

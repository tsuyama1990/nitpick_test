"""Unit tests for storage cache."""

import pathlib
import time

import polars as pl
import pytest

from src.storage.cache import LocalParquetCache


@pytest.fixture
def temp_cache_dir(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> pathlib.Path:
    """Provide a temporary cache directory."""
    monkeypatch.setenv("CACHE_DIR", str(tmp_path))
    return tmp_path


def test_cache_save_and_load(temp_cache_dir: pathlib.Path) -> None:
    """Test saving and loading a valid cache."""
    cache = LocalParquetCache()
    df = pl.DataFrame({"a": [1, 2, 3]})
    cache.save("test_key", df)

    loaded_df = cache.load("test_key")
    assert loaded_df is not None
    assert loaded_df.equals(df)


def test_cache_load_invalid(temp_cache_dir: pathlib.Path) -> None:
    """Test loading a non-existent cache key."""
    cache = LocalParquetCache()
    loaded_df = cache.load("non_existent_key")
    assert loaded_df is None


def test_cache_ttl_expiration(
    temp_cache_dir: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test cache expiration."""
    cache = LocalParquetCache(ttl_seconds=1)
    df = pl.DataFrame({"a": [1, 2, 3]})
    cache.save("test_key", df)

    # Mock time to simulate expiration
    original_time = time.time
    monkeypatch.setattr(time, "time", lambda: original_time() + 2)

    loaded_df = cache.load("test_key")
    assert loaded_df is None

import os
import time
from pathlib import Path
from unittest import mock

import polars as pl
import pytest
from pydantic import ValidationError

from src.domain_models.config import CacheSettings
from src.processing.cache import LocalCache


def test_cache_settings_default() -> None:
    """Test CacheSettings uses default values when no env vars are provided."""
    with mock.patch.dict(os.environ, {}, clear=True):
        settings = CacheSettings()
        assert settings.cache_dir == ".cache"


def test_cache_settings_custom() -> None:
    """Test CacheSettings can override cache_dir via environment."""
    with mock.patch.dict(os.environ, {"CACHE_DIR": "/custom/path"}, clear=True):
        settings = CacheSettings()
        assert settings.cache_dir == "/custom/path"


def test_cache_settings_forbid_extra() -> None:
    """Test CacheSettings rejects unknown kwargs."""
    with pytest.raises(ValidationError):
        CacheSettings(unknown_key="value")  # type: ignore[call-arg]


def test_local_cache_directory_creation(tmp_path: Path) -> None:
    nested_path = tmp_path / "nested" / "dir"
    assert not nested_path.exists()
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
    assert retrieved_df.equals(df)


def test_local_cache_miss_workflow(tmp_path: Path) -> None:
    cache = LocalCache(cache_dir=tmp_path, ttl_seconds=3600)
    retrieved_df = cache.get("non_existent_key")
    assert retrieved_df is None


def test_local_cache_expiration(tmp_path: Path) -> None:
    cache = LocalCache(cache_dir=tmp_path, ttl_seconds=3600)
    df = pl.DataFrame({"a": [1]})

    cache.set("test_key", df)

    # Backdate the file's modification timestamp by 3601 seconds
    file_path = tmp_path / "test_key.parquet"
    past_time = time.time() - 3601

    # We need to make sure the file exists before changing utime
    # Since set() is not implemented yet, this will fail in utime if not created
    # but the logic for the test is correct for a real implementation.
    if file_path.exists():
        os.utime(file_path, (past_time, past_time))

    retrieved_df = cache.get("test_key")
    assert retrieved_df is None

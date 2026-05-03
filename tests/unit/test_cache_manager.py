import os
import time
from pathlib import Path

import polars as pl

from src.processing.cache_manager import load_from_cache, save_to_cache


def test_cache_save_and_load(tmp_path: Path) -> None:
    # Setup test DataFrame
    df = pl.DataFrame({"test": [1, 2, 3]})
    repo_name = "test_owner_test_repo"

    # Save to cache
    save_to_cache(repo_name, df, cache_dir=tmp_path)

    # Verify file exists
    cache_file = tmp_path / f"{repo_name}_commits.parquet"
    assert cache_file.exists()

    # Load from cache
    loaded_df = load_from_cache(repo_name, cache_dir=tmp_path)
    assert loaded_df is not None
    assert loaded_df.equals(df)


def test_cache_miss(tmp_path: Path) -> None:
    loaded_df = load_from_cache("missing_repo", cache_dir=tmp_path)
    assert loaded_df is None


def test_cache_ttl_expiration(tmp_path: Path) -> None:
    df = pl.DataFrame({"test": [1]})
    repo_name = "ttl_test_repo"

    # Save to cache
    save_to_cache(repo_name, df, cache_dir=tmp_path)

    # Modify file access/modification time to 3601 seconds ago
    cache_file = tmp_path / f"{repo_name}_commits.parquet"
    past_time = time.time() - 3601
    os.utime(cache_file, (past_time, past_time))

    # Load from cache
    loaded_df = load_from_cache(repo_name, cache_dir=tmp_path, ttl_seconds=3600)
    assert loaded_df is None

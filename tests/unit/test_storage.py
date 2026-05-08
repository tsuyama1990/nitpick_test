import os
import pathlib
import time
from unittest.mock import patch

import polars as pl

from src.transformation.storage import load_from_cache, save_to_cache


def test_save_and_load_cache(tmp_path: pathlib.Path) -> None:
    df = pl.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})

    with patch.dict(os.environ, {"CACHE_DIR": str(tmp_path)}):
        # Save
        save_to_cache(df, "test_key")

        # Load
        loaded_df = load_from_cache("test_key")

        assert loaded_df is not None
        assert loaded_df.equals(df)


def test_load_cache_miss(tmp_path: pathlib.Path) -> None:
    with patch.dict(os.environ, {"CACHE_DIR": str(tmp_path)}):
        loaded_df = load_from_cache("non_existent_key")
        assert loaded_df is None


def test_load_cache_expired(tmp_path: pathlib.Path) -> None:
    df = pl.DataFrame({"a": [1]})

    with patch.dict(os.environ, {"CACHE_DIR": str(tmp_path)}):
        save_to_cache(df, "expired_key")
        cache_path = tmp_path / "expired_key.parquet"

        # Manipulate mtime to be strictly older than TTL
        old_time = time.time() - 3601
        os.utime(cache_path, (old_time, old_time))

        loaded_df = load_from_cache("expired_key")
        assert loaded_df is None

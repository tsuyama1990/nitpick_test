"""Unit tests for controller layer."""

from unittest.mock import patch

import polars as pl

from src.presentation.controller import _get_or_compute_cache
from src.storage.cache import LocalParquetCache


def test_get_or_compute_cache_hit() -> None:
    """Test cache hit branch."""
    df = pl.DataFrame({"test": [1]})

    with patch.object(LocalParquetCache, "load", return_value=df):
        cache = LocalParquetCache()
        result = _get_or_compute_cache(cache, "test_key", lambda: None, lambda x: None)
        assert result.equals(df)


def test_get_or_compute_cache_miss() -> None:
    df = pl.DataFrame({"test": [1]})
    with (
        patch.object(LocalParquetCache, "load", return_value=None),
        patch.object(LocalParquetCache, "save") as mock_save,
    ):
        cache = LocalParquetCache()
        result = _get_or_compute_cache(cache, "test_key", lambda: None, lambda x: df)
        assert result.equals(df)
        mock_save.assert_called_once_with("test_key", df)

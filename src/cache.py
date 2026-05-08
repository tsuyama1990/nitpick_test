"""Data caching module.

This module provides a caching mechanism using Parquet files and Polars DataFrames
to reduce the number of external API requests.
"""

import pathlib
import time

import polars as pl

from src.config import get_settings


class ParquetCache:
    """A TTL-based caching system for Polars DataFrames using Parquet files."""

    def __init__(self, ttl_seconds: int | None = None) -> None:
        """Initialize the cache with a specified or default TTL and directory."""
        self.settings = get_settings()
        self.ttl_seconds = (
            ttl_seconds if ttl_seconds is not None else self.settings.CACHE_TTL_SECONDS
        )

        if self.settings.CACHE_DIR:
            self.cache_dir = pathlib.Path(self.settings.CACHE_DIR)
        else:
            self.cache_dir = pathlib.Path.cwd() / ".cache" / "github_poc"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, key: str) -> pathlib.Path:
        """Construct a safe file path for a given cache key."""
        safe_key = key.replace("/", self.settings.CACHE_KEY_SEPARATOR)
        return self.cache_dir / f"{safe_key}{self.settings.CACHE_FILE_SUFFIX}"

    def is_valid(self, key: str) -> bool:
        """Check if the cache entry for the given key is still valid based on TTL."""
        file_path = self._get_file_path(key)
        if not file_path.exists():
            return False
        mtime = file_path.stat().st_mtime
        return (time.time() - mtime) <= self.ttl_seconds

    def load(self, key: str) -> pl.DataFrame | None:
        """Load a Polars DataFrame from the cache if it is still valid."""
        if not self.is_valid(key):
            return None
        return pl.read_parquet(self._get_file_path(key))

    def save(self, key: str, df: pl.DataFrame) -> None:
        """Save a Polars DataFrame to the cache."""
        df.write_parquet(self._get_file_path(key))

    def clear(self, key: str) -> None:
        """Remove a specific cache entry."""
        file_path = self._get_file_path(key)
        if file_path.exists():
            file_path.unlink()

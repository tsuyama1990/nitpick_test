"""Local caching using PyArrow and Parquet."""

import os
import pathlib
import time

import polars as pl


class LocalParquetCache:
    """Manages saving and loading Polars DataFrames to local Parquet files."""

    def __init__(self, ttl_seconds: int = 3600) -> None:
        """Initialize cache manager."""
        self.ttl_seconds = ttl_seconds
        cache_dir_env = os.getenv("CACHE_DIR")
        if cache_dir_env:
            self.cache_dir = pathlib.Path(cache_dir_env)
        else:
            self.cache_dir = pathlib.Path.cwd() / ".cache" / "github_dashboard"

        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_filepath(self, key: str) -> pathlib.Path:
        """Get the full filepath for a cache key."""
        return self.cache_dir / f"{key}.parquet"

    def is_valid(self, key: str) -> bool:
        """Check if a valid, unexpired cache exists for the given key."""
        filepath = self._get_filepath(key)
        if not filepath.exists():
            return False

        mtime = filepath.stat().st_mtime
        return not time.time() - mtime > self.ttl_seconds

    def save(self, key: str, df: pl.DataFrame) -> None:
        """Save a Polars DataFrame to cache."""
        filepath = self._get_filepath(key)
        df.write_parquet(filepath)

    def load(self, key: str) -> pl.DataFrame | None:
        """Load a Polars DataFrame from cache if valid."""
        if not self.is_valid(key):
            return None
        filepath = self._get_filepath(key)
        return pl.read_parquet(filepath)

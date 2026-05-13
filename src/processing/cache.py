import time
from pathlib import Path

import polars as pl


class LocalCache:
    """A local file-system based cache for Polars DataFrames using Parquet."""

    def __init__(self, cache_dir: str | Path | None = None, ttl_seconds: int | None = None) -> None:
        """
        Initialize the LocalCache.

        Args:
            cache_dir: The directory to store the cache files. Defaults to config if None.
            ttl_seconds: The time-to-live for cache entries in seconds. Defaults to config if None.
        """
        from src.config import get_cache_config

        config = get_cache_config()

        self.cache_dir = Path(cache_dir) if cache_dir is not None else config.cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_seconds if ttl_seconds is not None else config.cache_ttl_seconds

    def set(self, key: str, df: pl.DataFrame) -> None:
        """
        Save the DataFrame to the cache.

        Args:
            key: The key (filename) for the cache entry.
            df: The Polars DataFrame to store.
        """
        file_path = self.cache_dir / f"{key}.parquet"
        df.write_parquet(file_path)

    def get(self, key: str) -> pl.DataFrame | None:
        """
        Retrieve the DataFrame from the cache if it exists and is within the TTL.

        Args:
            key: The key for the cache entry.

        Returns:
            The cached Polars DataFrame, or None if the cache missed or expired.
        """
        file_path = self.cache_dir / f"{key}.parquet"

        if not file_path.exists():
            return None

        # Calculate the age of the file
        file_age = time.time() - file_path.stat().st_mtime

        if file_age > self.ttl_seconds:
            return None

        return pl.read_parquet(file_path)

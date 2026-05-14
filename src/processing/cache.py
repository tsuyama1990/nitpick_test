import time
from pathlib import Path

import polars as pl

from src.domain_models.config import CacheSettings


class LocalCache:
    """A local file-system caching layer tailored for Polars DataFrames."""

    def __init__(self, cache_dir: str | Path, ttl_seconds: int | None = None) -> None:
        """
        Initializes the cache directory and stores configuration.

        Args:
            cache_dir (str | Path): The directory where cache files will be stored.
            ttl_seconds (int | None): Time to live for cache files in seconds. Defaults to config.
        """
        settings = CacheSettings()
        self.cache_dir = Path(cache_dir)
        self.ttl_seconds = ttl_seconds if ttl_seconds is not None else settings.cache_ttl_seconds
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def set(self, key: str, df: pl.DataFrame) -> None:
        """
        Serializes a Polars DataFrame to a Parquet file.

        Args:
            key (str): The base file name for the cache entry.
            df (pl.DataFrame): The DataFrame to serialize.
        """
        file_path = self.cache_dir / f"{key}.parquet"
        df.write_parquet(file_path)

    def get(self, key: str) -> pl.DataFrame | None:
        """
        Retrieves a Polars DataFrame from the cache if it exists and is within the TTL window.

        Args:
            key (str): The base file name for the cache entry.

        Returns:
            pl.DataFrame | None: The deserialized DataFrame, or None if it's a cache miss or stale.
        """
        file_path = self.cache_dir / f"{key}.parquet"

        if not file_path.exists():
            return None

        file_age = time.time() - file_path.stat().st_mtime

        if file_age > self.ttl_seconds:
            return None

        return pl.read_parquet(file_path)

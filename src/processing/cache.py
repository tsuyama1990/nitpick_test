import time
from pathlib import Path

import polars as pl


class LocalCache:
    """A local file-system caching layer for Polars DataFrames using Parquet."""

    def __init__(self, cache_dir: str | Path | None = None, ttl_seconds: int | None = None) -> None:
        """Initialize the LocalCache with a directory and TTL."""
        from src.config import get_settings

        settings = get_settings()

        self.cache_dir = Path(cache_dir if cache_dir is not None else settings.cache_dir)
        self.ttl_seconds = ttl_seconds if ttl_seconds is not None else settings.cache_ttl
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def set(self, key: str, df: pl.DataFrame) -> None:
        """Serialize and save a Polars DataFrame to the cache."""
        file_path = self.cache_dir / f"{key}.parquet"
        df.write_parquet(file_path)

    def get(self, key: str) -> pl.DataFrame | None:
        """Retrieve a Polars DataFrame from the cache, respecting the TTL."""
        file_path = self.cache_dir / f"{key}.parquet"

        if not file_path.exists():
            return None

        # Retrieve the file's modification time
        file_mtime = file_path.stat().st_mtime
        current_time = time.time()
        age = current_time - file_mtime

        if age > self.ttl_seconds:
            return None

        return pl.read_parquet(file_path)

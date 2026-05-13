import time
from pathlib import Path

import polars as pl


class LocalCache:
    """A file-system caching layer tailored for Polars DataFrames using Parquet."""

    def __init__(self, cache_dir: str | Path, ttl_seconds: int = 3600) -> None:
        self.cache_dir = Path(cache_dir)
        self.ttl_seconds = ttl_seconds
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def set(self, key: str, df: pl.DataFrame) -> None:
        """Stores the DataFrame in the cache."""
        path = self.cache_dir / f"{key}.parquet"
        df.write_parquet(path)

    def get(self, key: str) -> pl.DataFrame | None:
        """Retrieves the DataFrame from the cache if it hasn't expired."""
        path = self.cache_dir / f"{key}.parquet"
        if not path.exists():
            return None

        file_age = time.time() - path.stat().st_mtime
        if file_age > self.ttl_seconds:
            return None

        return pl.read_parquet(path)

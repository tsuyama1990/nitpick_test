import time
from pathlib import Path

import polars as pl


class LocalCache:
    """A file-system caching layer tailored for Polars DataFrames."""

    def __init__(self, cache_dir: str | Path, ttl_seconds: int = 3600) -> None:
        """Initialize LocalCache, ensuring the cache_dir exists."""
        self.cache_dir = Path(cache_dir)
        self.ttl_seconds = ttl_seconds

        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def set(self, key: str, df: pl.DataFrame) -> None:
        """Serialize and store a DataFrame efficiently as a parquet file."""
        file_path = self.cache_dir / f"{key}.parquet"
        df.write_parquet(file_path)

    def get(self, key: str) -> pl.DataFrame | None:
        """Retrieve a DataFrame if it exists and hasn't expired."""
        file_path = self.cache_dir / f"{key}.parquet"

        if not file_path.exists():
            return None

        file_age = time.time() - file_path.stat().st_mtime

        if file_age > self.ttl_seconds:
            return None

        return pl.read_parquet(file_path)

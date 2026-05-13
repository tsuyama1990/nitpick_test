import time
from pathlib import Path

import polars as pl


class LocalCache:
    """Local file system cache for Polars DataFrames."""

    def __init__(self, cache_dir: str | Path, ttl_seconds: int = 3600) -> None:
        self.cache_dir = Path(cache_dir)
        self.ttl_seconds = ttl_seconds
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_path(self, key: str) -> Path:
        return self.cache_dir / f"{key}.parquet"

    def set(self, key: str, df: pl.DataFrame) -> None:
        """Stores a DataFrame to the cache."""
        path = self._get_path(key)
        df.write_parquet(path)

    def get(self, key: str) -> pl.DataFrame | None:
        """Retrieves a DataFrame from the cache if within TTL, else returns None."""
        path = self._get_path(key)
        if not path.exists():
            return None

        # Check TTL
        file_age = time.time() - path.stat().st_mtime
        if file_age > self.ttl_seconds:
            return None

        return pl.read_parquet(path)

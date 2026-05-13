import pathlib
import time

import polars as pl


class LocalCache:
    """A local file-system cache for Polars DataFrames using Parquet serialization."""

    def __init__(self, cache_dir: str | pathlib.Path, ttl_seconds: int = 3600) -> None:
        self.cache_dir = pathlib.Path(cache_dir)
        self.ttl_seconds = ttl_seconds
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, key: str) -> pathlib.Path:
        return self.cache_dir / f"{key}.parquet"

    def set(self, key: str, df: pl.DataFrame) -> None:
        """Serialize a Polars DataFrame to the local cache as a Parquet file."""
        file_path = self._get_file_path(key)
        df.write_parquet(file_path)

    def get(self, key: str) -> pl.DataFrame | None:
        """Retrieve a DataFrame from cache if it exists and is within the TTL window."""
        file_path = self._get_file_path(key)

        if not file_path.exists():
            return None

        file_age = time.time() - file_path.stat().st_mtime
        if file_age > self.ttl_seconds:
            return None

        return pl.read_parquet(file_path)

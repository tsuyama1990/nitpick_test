import contextlib
import os
import pathlib
import time

import polars as pl

from src.domain_models.config import get_settings


class CacheManager:
    def __init__(self, cache_dir_name: str | None = None, ttl_seconds: int = 3600) -> None:
        if cache_dir_name is None:
            cache_dir_name = get_settings().CACHE_DIR_NAME
        cache_base = os.getenv("CACHE_DIR", str(pathlib.Path.cwd() / ".cache" / cache_dir_name))
        self.cache_dir = pathlib.Path(cache_base)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_seconds

    def _get_cache_path(self, key: str) -> pathlib.Path:
        # Sanitize key to be safe for filenames
        safe_key = "".join(c if c.isalnum() else "_" for c in key)
        return self.cache_dir / f"{safe_key}.parquet"

    def save(self, key: str, df: pl.DataFrame) -> None:
        """Saves a Polars DataFrame to cache."""
        path = self._get_cache_path(key)
        df.write_parquet(path)

    def load(self, key: str) -> pl.DataFrame | None:
        """Loads a Polars DataFrame from cache if it exists and is valid."""
        path = self._get_cache_path(key)
        if not path.exists():
            return None

        # Check TTL
        file_age = time.time() - path.stat().st_mtime
        if file_age > self.ttl_seconds:
            # Optionally remove the expired file
            with contextlib.suppress(OSError):
                path.unlink()
            return None

        return pl.read_parquet(path)

import logging
import os
import pathlib
import time

import polars as pl

logger = logging.getLogger(__name__)


class CacheStorage:
    def __init__(
        self,
        cache_dir: str | None = None,
        ttl_seconds: int = 3600,
    ) -> None:
        if cache_dir is None:
            cache_dir = os.getenv("CACHE_DIR", str(pathlib.Path.cwd() / ".cache" / "github_dashboard"))
        self.cache_dir = pathlib.Path(cache_dir)
        self.ttl_seconds = ttl_seconds
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_path(self, key: str) -> pathlib.Path:
        return self.cache_dir / f"{key}.parquet"

    def get(self, key: str) -> pl.DataFrame | None:
        path = self._get_path(key)
        if not path.exists():
            return None

        mtime = path.stat().st_mtime
        if time.time() - mtime > self.ttl_seconds:
            logger.info(f"Cache expired for {key}")
            return None

        try:
            return pl.read_parquet(path)
        except Exception as e:
            logger.warning(f"Failed to read cache for {key}: {e}")
            return None

    def set(self, key: str, df: pl.DataFrame) -> None:
        path = self._get_path(key)
        try:
            df.write_parquet(path)
        except Exception as e:
            logger.warning(f"Failed to write cache for {key}: {e}")

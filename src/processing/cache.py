import pathlib
import time

import polars as pl

from src.domain_models.config import get_settings


class LocalCache:
    def __init__(self, cache_dir: str | pathlib.Path, ttl_seconds: int | None = None) -> None:
        settings = get_settings()
        self.cache_dir = pathlib.Path(cache_dir)
        self.ttl_seconds = ttl_seconds if ttl_seconds is not None else settings.CACHE_TTL_SECONDS
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def set_value(self, key: str, df: pl.DataFrame) -> None:
        path = self.cache_dir / f"{key}.parquet"
        df.write_parquet(path)

    def get(self, key: str) -> pl.DataFrame | None:
        path = self.cache_dir / f"{key}.parquet"
        if not path.exists():
            return None

        st_mtime = path.stat().st_mtime
        if time.time() - st_mtime > self.ttl_seconds:
            return None

        return pl.read_parquet(path)

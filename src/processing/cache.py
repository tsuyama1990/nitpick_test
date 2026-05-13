import pathlib
import time

import polars as pl


class LocalCache:
    def __init__(self, cache_dir: str | pathlib.Path, ttl_seconds: int = 3600) -> None:
        self.cache_dir = pathlib.Path(cache_dir)
        self.ttl_seconds = ttl_seconds
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def set(self, key: str, df: pl.DataFrame) -> None:
        path = self.cache_dir / f"{key}.parquet"
        df.write_parquet(path)

    def get(self, key: str) -> pl.DataFrame | None:
        path = self.cache_dir / f"{key}.parquet"
        if not path.exists():
            return None

        mtime = path.stat().st_mtime
        age = time.time() - mtime

        if age > self.ttl_seconds:
            return None

        return pl.read_parquet(path)

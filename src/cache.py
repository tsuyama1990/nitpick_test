import os
import pathlib
import time

import polars as pl


class ParquetCache:
    def __init__(self, ttl_seconds: int = 3600) -> None:
        self.ttl_seconds = ttl_seconds
        cache_dir_env = os.getenv("CACHE_DIR")
        if cache_dir_env:
            self.cache_dir = pathlib.Path(cache_dir_env)
        else:
            self.cache_dir = pathlib.Path.cwd() / ".cache" / "github_poc"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, key: str) -> pathlib.Path:
        safe_key = key.replace("/", "_")
        return self.cache_dir / f"{safe_key}.parquet"

    def is_valid(self, key: str) -> bool:
        file_path = self._get_file_path(key)
        if not file_path.exists():
            return False
        mtime = file_path.stat().st_mtime
        return (time.time() - mtime) <= self.ttl_seconds

    def load(self, key: str) -> pl.DataFrame | None:
        if not self.is_valid(key):
            return None
        return pl.read_parquet(self._get_file_path(key))

    def save(self, key: str, df: pl.DataFrame) -> None:
        df.write_parquet(self._get_file_path(key))

    def clear(self, key: str) -> None:
        file_path = self._get_file_path(key)
        if file_path.exists():
            file_path.unlink()

import os
import pathlib
import time

import polars as pl


class CacheManager:
    """Manages local Parquet file caching for DataFrames."""

    def __init__(self, ttl_seconds: int = 3600) -> None:
        cache_dir_env = os.getenv("CACHE_DIR")
        if cache_dir_env:
            self.cache_dir = pathlib.Path(cache_dir_env)
        else:
            self.cache_dir = pathlib.Path.cwd() / ".cache" / "github_dashboard"

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_seconds

    def _get_file_path(self, owner: str, repo: str, prefix: str) -> pathlib.Path:
        filename = f"{owner}_{repo}_{prefix}.parquet"
        return self.cache_dir / filename

    def is_valid(self, owner: str, repo: str, prefix: str) -> bool:
        """Checks if a valid cache file exists."""
        file_path = self._get_file_path(owner, repo, prefix)
        if not file_path.exists():
            return False

        mtime = file_path.stat().st_mtime
        return time.time() - mtime <= self.ttl_seconds

    def load(self, owner: str, repo: str, prefix: str) -> pl.DataFrame | None:
        """Loads a DataFrame from cache if valid."""
        if not self.is_valid(owner, repo, prefix):
            return None

        file_path = self._get_file_path(owner, repo, prefix)
        return pl.read_parquet(file_path)

    def save(self, df: pl.DataFrame, owner: str, repo: str, prefix: str) -> None:
        """Saves a DataFrame to cache."""
        file_path = self._get_file_path(owner, repo, prefix)
        df.write_parquet(file_path)

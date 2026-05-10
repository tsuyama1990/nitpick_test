import json
import os
import pathlib
import time
from typing import Any

import polars as pl


class CacheManager:
    def __init__(self, cache_dir_name: str = ".cache/app_data", ttl_seconds: int = 3600) -> None:
        # Fallback to local .cache if env var not set, preventing absolute path /tmp usage
        default_cache_dir = pathlib.Path.cwd() / cache_dir_name
        self.cache_dir = pathlib.Path(os.getenv("CACHE_DIR", default_cache_dir))
        self.ttl_seconds = ttl_seconds

        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, owner: str, repo: str, data_type: str) -> pathlib.Path:
        # data_type could be 'metrics' or 'commits'
        filename = f"{owner}_{repo}_{data_type}.parquet".replace("/", "_")
        return self.cache_dir / filename

    def is_valid(self, owner: str, repo: str, data_type: str) -> bool:
        """Check if the cache exists and is within the TTL."""
        file_path = self._get_file_path(owner, repo, data_type)
        if not file_path.exists():
            return False

        file_age = time.time() - file_path.stat().st_mtime
        return file_age < self.ttl_seconds

    def save_dataframe(self, owner: str, repo: str, data_type: str, df: pl.DataFrame) -> None:
        """Save a Polars DataFrame to Parquet format."""
        file_path = self._get_file_path(owner, repo, data_type)
        df.write_parquet(file_path)

    def load_dataframe(self, owner: str, repo: str, data_type: str) -> pl.DataFrame:
        """Load a Polars DataFrame from Parquet format."""
        file_path = self._get_file_path(owner, repo, data_type)
        if not file_path.exists():
            msg = f"Cache miss: File not found {file_path}"
            raise FileNotFoundError(msg)
        return pl.read_parquet(file_path)

    def save_json(self, owner: str, repo: str, data_type: str, data: dict[str, Any]) -> None:
        """Save a dictionary to JSON format."""
        file_path = self._get_file_path(owner, repo, data_type).with_suffix(".json")
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(data, f)

    def load_json(self, owner: str, repo: str, data_type: str) -> dict[str, Any]:
        """Load a dictionary from JSON format."""
        file_path = self._get_file_path(owner, repo, data_type).with_suffix(".json")
        if not file_path.exists():
            msg = f"Cache miss: File not found {file_path}"
            raise FileNotFoundError(msg)
        with file_path.open("r", encoding="utf-8") as f:
            res: dict[str, Any] = json.load(f)
            return res

    def is_valid_json(self, owner: str, repo: str, data_type: str) -> bool:
        """Check if the json cache exists and is within the TTL."""
        file_path = self._get_file_path(owner, repo, data_type).with_suffix(".json")
        if not file_path.exists():
            return False

        file_age = time.time() - file_path.stat().st_mtime
        return file_age < self.ttl_seconds

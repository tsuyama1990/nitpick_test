import json
import pathlib
import time
from typing import Any

import polars as pl

from src.config.settings import get_settings


class CacheManager:
    def __init__(self, ttl_seconds: int = 3600) -> None:
        settings = get_settings()
        self.cache_dir = pathlib.Path.cwd() / settings.CACHE_DIR
        self.ttl_seconds = ttl_seconds

        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_file_path(
        self, owner: str, repo: str, data_type: str, extension: str = "parquet"
    ) -> pathlib.Path:
        filename = f"{owner}_{repo}_{data_type}.{extension}".replace("/", "_")
        return self.cache_dir / filename

    def _is_cache_valid(self, file_path: pathlib.Path) -> bool:
        """Check if the file exists and is within the TTL."""
        if not file_path.exists():
            return False

        file_age = time.time() - file_path.stat().st_mtime
        return file_age < self.ttl_seconds

    def is_valid(self, owner: str, repo: str, data_type: str) -> bool:
        """Check if the Parquet cache exists and is within the TTL."""
        return self._is_cache_valid(self._get_file_path(owner, repo, data_type, "parquet"))

    def is_valid_json(self, owner: str, repo: str, data_type: str) -> bool:
        """Check if the JSON cache exists and is within the TTL."""
        return self._is_cache_valid(self._get_file_path(owner, repo, data_type, "json"))

    def save_dataframe(self, owner: str, repo: str, data_type: str, df: pl.DataFrame) -> None:
        """Save a Polars DataFrame to Parquet format."""
        file_path = self._get_file_path(owner, repo, data_type, "parquet")
        df.write_parquet(file_path)

    def load_dataframe(self, owner: str, repo: str, data_type: str) -> pl.DataFrame:
        """Load a Polars DataFrame from Parquet format."""
        file_path = self._get_file_path(owner, repo, data_type, "parquet")
        if not file_path.exists():
            msg = f"Cache miss: File not found {file_path}"
            raise FileNotFoundError(msg)
        return pl.read_parquet(file_path)

    def save_json(self, owner: str, repo: str, data_type: str, data: dict[str, Any]) -> None:
        """Save a dictionary to JSON format."""
        file_path = self._get_file_path(owner, repo, data_type, "json")
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(data, f)

    def load_json(self, owner: str, repo: str, data_type: str) -> dict[str, Any]:
        """Load a dictionary from JSON format."""
        file_path = self._get_file_path(owner, repo, data_type, "json")
        if not file_path.exists():
            msg = f"Cache miss: File not found {file_path}"
            raise FileNotFoundError(msg)
        with file_path.open("r", encoding="utf-8") as f:
            res: dict[str, Any] = json.load(f)
            return res

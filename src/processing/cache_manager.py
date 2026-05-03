import time
from pathlib import Path

import polars as pl

from src.config import settings


def _get_cache_filepath(repo_name: str, cache_dir: Path | None = None) -> Path:
    repo_safe_name = repo_name.replace("/", "_")
    base_dir = cache_dir if cache_dir is not None else settings.cache_dir
    return base_dir / f"{repo_safe_name}_commits.parquet"


def save_to_cache(repo_name: str, df: pl.DataFrame, cache_dir: Path | None = None) -> None:
    """Saves a Polars DataFrame to a parquet file in the cache directory."""
    filepath = _get_cache_filepath(repo_name, cache_dir)
    # Ensure directory exists just in case
    filepath.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(filepath)


def load_from_cache(
    repo_name: str, cache_dir: Path | None = None, ttl_seconds: int | None = None
) -> pl.DataFrame | None:
    """Loads a Polars DataFrame from the cache if it exists and is within TTL."""
    filepath = _get_cache_filepath(repo_name, cache_dir)

    if not filepath.exists():
        return None

    mtime = filepath.stat().st_mtime
    current_time = time.time()
    ttl = ttl_seconds if ttl_seconds is not None else settings.cache_ttl_seconds

    if (current_time - mtime) > ttl:
        return None

    return pl.read_parquet(filepath)

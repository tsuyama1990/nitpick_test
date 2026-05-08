import os
import pathlib
import time

import polars as pl

CACHE_TTL_SECONDS = 3600  # 1 hour


def _get_cache_dir() -> pathlib.Path:
    cache_dir = os.getenv("CACHE_DIR", str(pathlib.Path.cwd() / ".cache" / "github_dashboard"))
    path = pathlib.Path(cache_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_to_cache(df: pl.DataFrame, key: str) -> None:
    """Save a Polars DataFrame to a local parquet file as a cache."""
    cache_path = _get_cache_dir() / f"{key}.parquet"
    df.write_parquet(cache_path)


def load_from_cache(key: str) -> pl.DataFrame | None:
    """Load a Polars DataFrame from a local parquet file if it exists and is within TTL."""
    cache_path = _get_cache_dir() / f"{key}.parquet"
    if not cache_path.exists():
        return None

    # Check TTL
    file_mtime = cache_path.stat().st_mtime
    if time.time() - file_mtime > CACHE_TTL_SECONDS:
        return None

    return pl.read_parquet(cache_path)

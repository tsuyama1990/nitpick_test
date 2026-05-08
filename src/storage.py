import os
import pathlib
import time

import polars as pl


def _get_cache_dir() -> pathlib.Path:
    cache_dir_str = os.getenv("CACHE_DIR")
    if cache_dir_str:
        cache_dir = pathlib.Path(cache_dir_str)
    else:
        cache_dir = pathlib.Path.cwd() / ".cache" / "github_poc"

    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def _is_cache_valid(filepath: pathlib.Path, ttl_seconds: int = 3600) -> bool:
    if not filepath.exists():
        return False
    file_mtime = filepath.stat().st_mtime
    return time.time() - file_mtime < ttl_seconds


def load_cached_dataframe(cache_key: str, ttl_seconds: int = 3600) -> pl.DataFrame | None:
    cache_dir = _get_cache_dir()
    filepath = cache_dir / f"{cache_key}.parquet"
    if _is_cache_valid(filepath, ttl_seconds):
        return pl.read_parquet(filepath)
    return None


def save_dataframe_to_cache(df: pl.DataFrame, cache_key: str) -> None:
    cache_dir = _get_cache_dir()
    filepath = cache_dir / f"{cache_key}.parquet"
    df.write_parquet(filepath)

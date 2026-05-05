import json
import time
from pathlib import Path
from typing import Any

import polars as pl

CACHE_DIR = Path(".cache")
TTL_SECONDS = 3600  # 1 hour TTL


def _get_cache_path(key: str) -> Path:
    """Generates a file path for a cache key."""
    if not CACHE_DIR.exists():
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"{key.replace('/', '_')}.parquet"


def save_to_cache(key: str, df: pl.DataFrame) -> None:
    """Saves a Polars DataFrame to a Parquet file."""
    path = _get_cache_path(key)
    df.write_parquet(path)


def save_metadata_cache(key: str, data: dict[str, Any]) -> None:
    """Saves dictionary metadata to a JSON file."""
    path = CACHE_DIR / f"{key.replace('/', '_')}.json"
    with path.open("w") as f:
        json.dump(data, f)


def load_metadata_cache(key: str) -> dict[str, Any] | None:
    """Loads dictionary metadata from a JSON file if within TTL."""
    path = CACHE_DIR / f"{key.replace('/', '_')}.json"
    if not path.exists():
        return None

    file_age = time.time() - path.stat().st_mtime
    if file_age > TTL_SECONDS:
        path.unlink()
        return None

    try:
        with path.open() as f:
            res: dict[str, Any] = json.load(f)
            return res
    except Exception:
        path.unlink()
        return None


def load_from_cache(key: str) -> pl.DataFrame | None:
    """Loads a Polars DataFrame from a Parquet file if within TTL."""
    path = _get_cache_path(key)
    if not path.exists():
        return None

    file_age = time.time() - path.stat().st_mtime
    if file_age > TTL_SECONDS:
        path.unlink()  # Remove expired cache
        return None

    try:
        return pl.read_parquet(path)
    except Exception:
        # If cache is corrupted, delete it
        path.unlink()
        return None

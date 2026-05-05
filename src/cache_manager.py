import time
from pathlib import Path

import polars as pl

from src.domain_models import get_settings


def _get_cache_filepath(repo_name: str) -> Path:
    """Generate the local cache file path for a given repository name."""
    settings = get_settings()
    cache_dir = Path(settings.CACHE_DIR)

    # Ensure directory exists
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Sanitize repo name
    safe_name = repo_name.replace("/", "_").replace("\\", "_")
    return cache_dir / f"{safe_name}_commits.parquet"


def save_to_cache(repo_name: str, df: pl.DataFrame) -> None:
    """Save the Polars DataFrame to a local Parquet file."""
    if df is None:
        return

    cache_file = _get_cache_filepath(repo_name)
    df.write_parquet(cache_file)


def load_from_cache(repo_name: str) -> pl.DataFrame | None:
    """
    Load a cached DataFrame if it exists and hasn't expired according to TTL.
    Returns None if cache is expired, invalid, or doesn't exist.
    """
    cache_file = _get_cache_filepath(repo_name)

    if not cache_file.exists():
        return None

    try:
        # Check TTL
        mtime = cache_file.stat().st_mtime
        settings = get_settings()
        if time.time() - mtime > settings.CACHE_TTL_SECONDS:
            return None

        return pl.read_parquet(cache_file)
    except Exception:
        # In case of corruption or other read error, act as cache miss
        return None

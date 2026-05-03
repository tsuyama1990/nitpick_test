import logging
from collections.abc import Callable

import polars as pl

from src.domain_models import CommitRecord
from src.processing.cache_manager import load_from_cache, save_to_cache
from src.processing.transformer import calculate_daily_commits

logger = logging.getLogger(__name__)


def orchestrate_repository_processing(
    repo_name: str, fetch_func: Callable[[str], list[CommitRecord]]
) -> pl.DataFrame:
    """Orchestrates the checking of cache, fallback to API, and saving results."""
    cached_df = load_from_cache(repo_name)
    if cached_df is not None:
        return cached_df

    records = fetch_func(repo_name)
    df = calculate_daily_commits(records)
    save_to_cache(repo_name, df)
    return df


def run_app() -> None:
    logger.info("Application initialized. Ready to process repositories.")

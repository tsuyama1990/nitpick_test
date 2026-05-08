"""Controller orchestrating data ingestion, transformation and storage."""

import logging
from typing import Any

import polars as pl

from src.domain_models.manifest import CommitInfo, RepoInfo
from src.ingestion.github_client import get_repo_commits, get_repo_info
from src.storage.cache import LocalParquetCache
from src.transformation.metrics import aggregate_daily_commits, get_top_committers

logger = logging.getLogger(__name__)


def _get_or_compute_cache(
    cache: LocalParquetCache, key: str, fetch_func: Any, transform_func: Any
) -> pl.DataFrame:
    """Helper to check cache and compute if missed."""
    df = cache.load(key)
    if df is not None:
        logger.info(f"Cache hit for {key}")
        return df

    logger.info(f"Cache miss for {key}. Fetching and transforming data.")
    raw_data = fetch_func()
    # Apply transformation
    df = transform_func(raw_data)
    cache.save(key, df)
    return df  # type: ignore[no-any-return]


def get_dashboard_data(owner: str, repo: str) -> tuple[RepoInfo, pl.DataFrame, pl.DataFrame]:
    """Get the full dashboard data, utilizing cache where appropriate."""
    cache = LocalParquetCache()
    repo_key = f"{owner}_{repo}"

    # 1. Fetch Repository Info
    repo_info_key = f"{repo_key}_repo_info"
    repo_df = cache.load(repo_info_key)
    if repo_df is None:
        logger.info(f"Cache miss for {repo_info_key}. Fetching from API.")
        raw_repo = get_repo_info(owner, repo)
        # Convert to DataFrame to cache via parquet
        repo_df = pl.DataFrame([raw_repo])
        cache.save(repo_info_key, repo_df)
    else:
        logger.info(f"Cache hit for {repo_info_key}.")
        # Convert back to dict to pass to Pydantic model
        raw_repo = repo_df.to_dicts()[0]

    repo_info = RepoInfo(
        stargazers_count=raw_repo.get("stargazers_count", 0),
        forks_count=raw_repo.get("forks_count", 0),
        open_issues_count=raw_repo.get("open_issues_count", 0),
    )

    # 2. Fetch Commits (Heavier, cache it)
    def fetch_commits() -> list[dict[str, Any]]:
        raw_commits = get_repo_commits(owner, repo, per_page=100)
        # Flatten using domain model
        return [CommitInfo(**c).model_dump() for c in raw_commits]

    # Daily commits
    daily_key = f"{repo_key}_daily_commits"

    # Top committers
    top_key = f"{repo_key}_top_committers"
    # We can optimize by reusing fetch_commits instead of fetching twice,
    # but the cache function will hit network on first if not careful.
    # To prevent double fetching on miss, fetch once if either is missing:

    daily_df = cache.load(daily_key)
    top_df = cache.load(top_key)

    if daily_df is None or top_df is None:
        logger.info(f"Cache miss for commits of {repo_key}. Fetching from API.")
        flat_commits = fetch_commits()
        daily_df = aggregate_daily_commits(flat_commits)
        top_df = get_top_committers(flat_commits)
        cache.save(daily_key, daily_df)
        cache.save(top_key, top_df)
    else:
        logger.info(f"Cache hit for commits of {repo_key}.")

    return repo_info, daily_df, top_df

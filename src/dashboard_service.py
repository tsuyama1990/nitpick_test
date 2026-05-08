"""Dashboard orchestration service.

This module acts as an orchestrator, connecting the GitHub API client,
the Polars data transformation logic, and the local Parquet caching layer.
"""

from typing import Any

import polars as pl

from src.cache import ParquetCache
from src.github_client import GitHubClient
from src.metrics import MetricsTransformer


class DashboardService:
    """Service layer coordinating API fetching, transformation, and caching."""

    def __init__(self) -> None:
        """Initialize the dashboard service with its required dependencies."""
        self.api_client = GitHubClient()
        self.transformer = MetricsTransformer()
        self.cache = ParquetCache()

    def get_repo_metrics(self, owner: str, repo: str) -> dict[str, Any]:
        """Fetch general repository metrics directly from the API client."""
        return self.api_client.get_repo_metrics(owner, repo)

    def get_commit_data(self, owner: str, repo: str) -> tuple[pl.DataFrame, pl.DataFrame]:
        """Fetch and aggregate commit data, utilizing the cache if available."""
        cache_key_date = f"{owner}_{repo}_commits_by_date"
        cache_key_top = f"{owner}_{repo}_top_committers"

        if self.cache.is_valid(cache_key_date) and self.cache.is_valid(cache_key_top):
            df_by_date = self.cache.load(cache_key_date)
            df_top = self.cache.load(cache_key_top)
            if df_by_date is not None and df_top is not None:
                return df_by_date, df_top

        raw = self.api_client.get_commits(owner, repo)
        df = self.transformer.process_commits(raw)
        df_by_date = self.transformer.aggregate_commits_by_date(df)
        df_top = self.transformer.get_top_committers(df)

        self.cache.save(cache_key_date, df_by_date)
        self.cache.save(cache_key_top, df_top)
        return df_by_date, df_top

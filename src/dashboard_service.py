from typing import Any

import polars as pl

from src.cache import ParquetCache
from src.github_client import GitHubClient
from src.metrics import MetricsTransformer


class DashboardService:
    def __init__(self) -> None:
        self.api_client = GitHubClient()
        self.transformer = MetricsTransformer()
        self.cache = ParquetCache()

    def get_repo_metrics(self, owner: str, repo: str) -> dict[str, Any]:
        return self.api_client.get_repo_metrics(owner, repo)

    def get_commit_data(self, owner: str, repo: str) -> tuple[pl.DataFrame, pl.DataFrame]:
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

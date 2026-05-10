from dataclasses import dataclass

import polars as pl

from src.domain_models.repository import RepoMetrics
from src.ingestion.github_client import GitHubAPIClient
from src.storage.cache import CacheManager
from src.transformation.metrics import (
    aggregate_daily_commits,
    aggregate_top_committers,
    commits_to_dataframe,
)


@dataclass
class DashboardData:
    metrics: RepoMetrics
    daily_commits: pl.DataFrame
    top_committers: pl.DataFrame


class DashboardController:
    def __init__(self) -> None:
        self.api_client = GitHubAPIClient()
        self.cache_manager = CacheManager()

    def get_dashboard_data(self, owner: str, repo: str) -> DashboardData:
        # 1. Fetch or Load Repo Metrics
        if self.cache_manager.is_valid_json(owner, repo, "metrics"):
            metrics_dict = self.cache_manager.load_json(owner, repo, "metrics")
            metrics = RepoMetrics(**metrics_dict)
        else:
            metrics = self.api_client.fetch_repo_metrics(owner, repo)
            # The model dumping ensures we cache exactly what we need, including open_issues.
            self.cache_manager.save_json(owner, repo, "metrics", metrics.model_dump())

        # 2. Check Cache for Transformed Commit Data
        if self.cache_manager.is_valid(owner, repo, "daily_commits") and self.cache_manager.is_valid(owner, repo, "top_committers"):
            daily_commits = self.cache_manager.load_dataframe(owner, repo, "daily_commits")
            top_committers = self.cache_manager.load_dataframe(owner, repo, "top_committers")
        else:
            # 3. Cache Miss: Fetch from GitHub
            raw_commits = self.api_client.fetch_recent_commits(owner, repo)

            # Convert objects to dicts for Polars
            commits_data: list[dict[str, str | pl.Datetime]] = [
                {"date": c.date.strftime("%Y-%m-%dT%H:%M:%SZ"), "author_name": c.author_name}
                for c in raw_commits
            ]

            # 4. Transform Data
            df_commits = commits_to_dataframe(commits_data)
            daily_commits = aggregate_daily_commits(df_commits)
            top_committers = aggregate_top_committers(df_commits)

            # 5. Save to Cache
            self.cache_manager.save_dataframe(owner, repo, "daily_commits", daily_commits)
            self.cache_manager.save_dataframe(owner, repo, "top_committers", top_committers)

        return DashboardData(
            metrics=metrics,
            daily_commits=daily_commits,
            top_committers=top_committers
        )

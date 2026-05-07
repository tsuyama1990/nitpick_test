import logging

import polars as pl

from src.domain_models import Repository
from src.ingestion.client import GitHubClient, GitHubClientError
from src.storage.cache import CacheStorage
from src.transformation.processor import DataTransformer

logger = logging.getLogger(__name__)

class DashboardController:
    def __init__(self) -> None:
        self.client = GitHubClient()
        self.transformer = DataTransformer()
        self.cache = CacheStorage()

    def get_dashboard_data(self, owner: str, repo: str) -> tuple[Repository | None, pl.DataFrame | None, pl.DataFrame | None, str | None]:
        """
        Orchestrates fetching repository data and commits.
        Returns: (Repository, commits_by_date, top_committers, error_message)
        """
        try:
            repo_info = self.client.get_repository_info(owner, repo)
        except GitHubClientError as e:
            return None, None, None, str(e)

        cache_key_date = f"{owner}_{repo}_commits_by_date"
        cache_key_users = f"{owner}_{repo}_top_committers"

        cached_date = self.cache.get(cache_key_date)
        cached_users = self.cache.get(cache_key_users)

        if cached_date is not None and cached_users is not None:
            logger.info("Cache hit for commits.")
            return repo_info, cached_date, cached_users, None

        try:
            commits = self.client.get_recent_commits(owner, repo)
        except GitHubClientError as e:
            return repo_info, None, None, str(e)

        commits_by_date, top_committers = self.transformer.process_commits(commits)

        self.cache.set(cache_key_date, commits_by_date)
        self.cache.set(cache_key_users, top_committers)

        return repo_info, commits_by_date, top_committers, None

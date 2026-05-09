import json
import pathlib
import time
from typing import Any

import polars as pl

from src.clients.github_client import GitHubClient
from src.domain_models.config import get_settings
from src.domain_models.github import RepoInfo


class DataProcessor:
    """Orchestrator for fetching GitHub data, processing via Polars, and caching."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = GitHubClient()
        self.cache_dir = self.settings.CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = 3600  # 1 hour

    def is_cache_valid(self, cache_file: pathlib.Path) -> bool:
        """Checks if a cache file is valid based on TTL."""
        if not cache_file.exists():
            return False
        mtime = cache_file.stat().st_mtime
        return (time.time() - mtime) < self.ttl

    def get_repo_data(self, owner: str, repo: str) -> RepoInfo:
        """Retrieves repository info, from cache if valid."""
        cache_file = self.cache_dir / f"{owner}_{repo}_repo.json"

        if self.is_cache_valid(cache_file):
            with cache_file.open(encoding="utf-8") as f:
                res: dict[str, Any] = json.load(f)
                return RepoInfo.model_validate(res)

        repo_info = self.client.get_repo_info(owner, repo)

        with cache_file.open("w", encoding="utf-8") as f:
            json.dump(repo_info.model_dump(), f)

        return repo_info

    def get_commit_data(self, owner: str, repo: str) -> tuple[pl.DataFrame, pl.DataFrame]:
        """Returns DataFrames for commits by date and top committers."""
        cache_date_file = self.cache_dir / f"{owner}_{repo}_commits_date.parquet"
        cache_user_file = self.cache_dir / f"{owner}_{repo}_commits_user.parquet"

        if self.is_cache_valid(cache_date_file) and self.is_cache_valid(cache_user_file):
            df_date = pl.read_parquet(cache_date_file)
            df_user = pl.read_parquet(cache_user_file)
            return df_date, df_user

        commits = self.client.get_commits(owner, repo)

        if not commits:
            df = pl.DataFrame({"sha": [], "author_name": [], "date": []})
        else:
            df = pl.DataFrame([c.model_dump() for c in commits])

        df_date = self._aggregate_commits_by_date(df)
        df_user = self._aggregate_top_committers(df)

        df_date.write_parquet(cache_date_file)
        df_user.write_parquet(cache_user_file)

        return df_date, df_user

    def _aggregate_commits_by_date(self, df: pl.DataFrame) -> pl.DataFrame:
        """Aggregates commit counts by date."""
        if df.is_empty():
            return pl.DataFrame(schema={"date_only": pl.Date, "commit_count": pl.UInt32})

        df_clean = df.with_columns(pl.col("date").str.slice(0, 10).cast(pl.Date).alias("date_only"))
        return df_clean.group_by("date_only").agg(pl.len().alias("commit_count")).sort("date_only")

    def _aggregate_top_committers(self, df: pl.DataFrame) -> pl.DataFrame:
        """Aggregates commit counts by user, returning top 5."""
        if df.is_empty():
            return pl.DataFrame(schema={"author_name": pl.String, "commit_count": pl.UInt32})

        return (
            df.group_by("author_name")
            .agg(pl.len().alias("commit_count"))
            .sort("commit_count", descending=True)
            .head(5)
        )

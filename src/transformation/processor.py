import logging
import time
from pathlib import Path

import polars as pl

from src.domain_models import CommitInfo, get_settings

logger = logging.getLogger(__name__)


class DataProcessor:
    """Processes and caches GitHub API data."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.cache_dir = Path(self.settings.CACHE_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_ttl = 3600  # 1 hour

    def _is_cache_valid(self, filepath: Path) -> bool:
        """Checks if a cache file exists and is within the TTL."""
        if not filepath.exists():
            return False
        mtime = filepath.stat().st_mtime
        return (time.time() - mtime) < self.cache_ttl

    def process_daily_commits(
        self, owner: str, repo: str, commits: list[CommitInfo] | None = None
    ) -> pl.DataFrame:
        """
        Calculates commits per day. Uses cache if available and commits are not explicitly provided.
        """
        cache_file = self.cache_dir / f"{owner}_{repo}_daily_commits.parquet"

        if commits is None:
            if self._is_cache_valid(cache_file):
                logger.info(f"Loading daily commits from cache: {cache_file}")
                return pl.read_parquet(cache_file)
            msg = "No valid cache found and no commits provided."
            raise ValueError(msg)

        # Transform logic
        df = pl.DataFrame([c.model_dump() for c in commits])

        # Format dates properly as string or Date
        if "committer_date" in df.columns:
            # We want YYYY-MM-DD
            daily_df = (
                df.with_columns(pl.col("committer_date").dt.date().alias("date"))
                .group_by("date")
                .len()
                .rename({"len": "commit_count"})
                .sort("date")
            )
        else:
            # Fallback if empty
            daily_df = pl.DataFrame({"date": [], "commit_count": []})

        # Save to cache
        logger.info(f"Saving daily commits to cache: {cache_file}")
        daily_df.write_parquet(cache_file)

        return daily_df

    def process_top_committers(
        self, owner: str, repo: str, commits: list[CommitInfo] | None = None
    ) -> pl.DataFrame:
        """
        Calculates top 5 committers. Uses cache if available and commits are not explicitly provided.
        """
        cache_file = self.cache_dir / f"{owner}_{repo}_top_committers.parquet"

        if commits is None:
            if self._is_cache_valid(cache_file):
                logger.info(f"Loading top committers from cache: {cache_file}")
                return pl.read_parquet(cache_file)
            msg = "No valid cache found and no commits provided."
            raise ValueError(msg)

        # Transform logic
        df = pl.DataFrame([c.model_dump() for c in commits])

        if "committer_name" in df.columns:
            top_df = (
                df.group_by("committer_name")
                .len()
                .rename({"len": "commit_count"})
                .sort("commit_count", descending=True)
                .head(5)
            )
        else:
            top_df = pl.DataFrame({"committer_name": [], "commit_count": []})

        # Save to cache
        logger.info(f"Saving top committers to cache: {cache_file}")
        top_df.write_parquet(cache_file)

        return top_df

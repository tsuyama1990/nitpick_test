"""Data transformation metrics module.

This module is responsible for transforming and aggregating raw GitHub commit
data using Polars for high-performance data manipulation.
"""

from typing import Any

import polars as pl

from src.domain_models.github import Commit


class MetricsTransformer:
    """Service for processing and transforming raw commit data into aggregated metrics."""

    def process_commits(self, raw_commits: list[dict[str, Any]]) -> pl.DataFrame:
        """Convert a list of raw commit dictionaries into a structured Polars DataFrame."""
        if not raw_commits:
            return pl.DataFrame(schema={"date": pl.Date, "name": pl.Utf8})
        valid = [Commit(**c) for c in raw_commits]
        return pl.DataFrame([{"date": c.date.date(), "name": c.name} for c in valid])

    def aggregate_commits_by_date(self, df: pl.DataFrame) -> pl.DataFrame:
        """Aggregate the commit DataFrame by date, returning a daily commit count."""
        if df.is_empty():
            return pl.DataFrame(schema={"date": pl.Date, "commits_count": pl.UInt32})
        return df.group_by("date").agg(pl.len().alias("commits_count")).sort("date")

    def get_top_committers(self, df: pl.DataFrame, top_n: int = 5) -> pl.DataFrame:
        """Identify the top committers and return their total commit counts."""
        if df.is_empty():
            return pl.DataFrame(schema={"name": pl.Utf8, "commits_count": pl.UInt32})
        return (
            df.group_by("name")
            .agg(pl.len().alias("commits_count"))
            .sort("commits_count", descending=True)
            .head(top_n)
        )

from typing import Any

import polars as pl

from src.domain_models.github import Commit


class MetricsTransformer:
    def process_commits(self, raw_commits: list[dict[str, Any]]) -> pl.DataFrame:
        if not raw_commits:
            return pl.DataFrame(schema={"date": pl.Date, "name": pl.Utf8})
        valid = [Commit(**c) for c in raw_commits]
        return pl.DataFrame([{"date": c.date.date(), "name": c.name} for c in valid])

    def aggregate_commits_by_date(self, df: pl.DataFrame) -> pl.DataFrame:
        if df.is_empty():
            return pl.DataFrame(schema={"date": pl.Date, "commits_count": pl.UInt32})
        return df.group_by("date").agg(pl.len().alias("commits_count")).sort("date")

    def get_top_committers(self, df: pl.DataFrame, top_n: int = 5) -> pl.DataFrame:
        if df.is_empty():
            return pl.DataFrame(schema={"name": pl.Utf8, "commits_count": pl.UInt32})
        return (
            df.group_by("name")
            .agg(pl.len().alias("commits_count"))
            .sort("commits_count", descending=True)
            .head(top_n)
        )

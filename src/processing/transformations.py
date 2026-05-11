from typing import Any

import polars as pl

from src.domain_models.schemas import CommitItem


def aggregate_commits_by_date(raw_commits: list[dict[str, Any]]) -> pl.DataFrame:
    """Aggregates commit counts by date."""
    validated_data = []
    for commit in raw_commits:
        stripped = CommitItem._strip_extra(commit)
        item = CommitItem(**stripped)
        validated_data.append(
            {
                "date": item.commit.author.date,
                "name": item.commit.author.name,
            }
        )

    if not validated_data:
        return pl.DataFrame(
            {"date": [], "commit_count": []}, schema={"date": pl.Date, "commit_count": pl.UInt32}
        )

    df = pl.DataFrame(validated_data)

    return (
        df.with_columns(pl.col("date").str.slice(0, 10).cast(pl.Date))
        .group_by("date")
        .agg(pl.len().alias("commit_count"))
        .sort("date")
    )


def get_top_committers(raw_commits: list[dict[str, Any]], top_n: int = 5) -> pl.DataFrame:
    """Gets top committers with deterministic sorting."""
    validated_data = []
    for commit in raw_commits:
        stripped = CommitItem._strip_extra(commit)
        item = CommitItem(**stripped)
        validated_data.append(
            {
                "name": item.commit.author.name,
            }
        )

    if not validated_data:
        return pl.DataFrame(
            {"name": [], "commit_count": []}, schema={"name": pl.String, "commit_count": pl.UInt32}
        )

    df = pl.DataFrame(validated_data)

    return (
        df.group_by("name")
        .agg(pl.len().alias("commit_count"))
        .sort(["commit_count", "name"], descending=[True, False])
        .head(top_n)
    )

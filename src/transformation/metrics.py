"""Metrics calculation using Polars."""

from typing import Any

import polars as pl


def aggregate_daily_commits(commits_data: list[dict[str, Any]]) -> pl.DataFrame:
    """Aggregate commits by date.

    Expected input is a list of dictionaries with 'date' and 'committer' keys,
    which have been extracted/flattened from the raw JSON payload.
    """
    if not commits_data:
        return pl.DataFrame(
            {"date": pl.Series(dtype=pl.Date), "commits": pl.Series(dtype=pl.Int64)}
        )

    df = pl.DataFrame(commits_data)

    # Cast the 'date' column to Date type
    df = df.with_columns(
        pl.col("date").str.to_datetime("%Y-%m-%dT%H:%M:%SZ", strict=False).dt.date().alias("date")
    )

    # Group by date and count
    return df.group_by("date").len(name="commits").sort("date")


def get_top_committers(commits_data: list[dict[str, Any]], top_n: int = 5) -> pl.DataFrame:
    """Get the top N committers by commit count."""
    if not commits_data:
        return pl.DataFrame(
            {"committer": pl.Series(dtype=pl.String), "commits": pl.Series(dtype=pl.Int64)}
        )

    df = pl.DataFrame(commits_data)

    # Group by committer and count
    return (
        df.group_by("committer")
        .len(name="commits")
        .sort(by=["commits", "committer"], descending=[True, False])
        .head(top_n)
    )

from typing import Any

import polars as pl

from src.domain_models import CommitItem


def _validate_and_flatten(raw_commits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Validates raw commits against CommitItem schema and returns flattened dicts."""
    flattened = []
    for commit_data in raw_commits:
        # Strict validation
        # We know we are unpacking from raw json, so we explicitly map required fields
        date_str = str(commit_data.get("date", ""))
        name_str = str(commit_data.get("name", ""))
        item = CommitItem(date=date_str, name=name_str)  # type: ignore[arg-type]
        flattened.append({"date": item.date, "name": item.name})
    return flattened


def aggregate_commits_by_date(raw_commits: list[dict[str, Any]]) -> pl.DataFrame:
    """Aggregates commits by date and returns a Polars DataFrame.

    Args:
        raw_commits: A list of dicts.

    Returns:
        A Polars DataFrame with 'date' and 'commit_count' columns.
    """
    if not raw_commits:
        return pl.DataFrame({"date": [], "commit_count": []}).with_columns(
            pl.col("date").cast(pl.Date),
            pl.col("commit_count").cast(pl.UInt32),
        )

    flattened = _validate_and_flatten(raw_commits)
    df = pl.DataFrame(flattened)

    return (
        df.with_columns(pl.col("date").cast(pl.Date))
        .group_by("date")
        .agg(pl.len().alias("commit_count"))
        .sort("date")
    )


def get_top_committers(raw_commits: list[dict[str, Any]], top_n: int = 5) -> pl.DataFrame:
    """Gets the top committers and returns a Polars DataFrame.

    Args:
        raw_commits: A list of dicts.
        top_n: Number of top committers to return.

    Returns:
        A Polars DataFrame with top committers.
    """
    if not raw_commits:
        return pl.DataFrame({"name": [], "commit_count": []}).with_columns(
            pl.col("name").cast(pl.Utf8),
            pl.col("commit_count").cast(pl.UInt32),
        )

    flattened = _validate_and_flatten(raw_commits)
    df = pl.DataFrame(flattened)

    return (
        df.group_by("name")
        .agg(pl.len().alias("commit_count"))
        .sort(["commit_count", "name"], descending=[True, False])
        .head(top_n)
    )

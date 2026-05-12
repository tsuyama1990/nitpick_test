from typing import Any

import polars as pl

from src.domain_models.config import config
from src.domain_models.schemas import CommitItem


def _extract_valid_commits(raw_commits: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Validates raw GitHub payloads and extracts flat commit attributes."""
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
    return validated_data


def aggregate_commits_by_date(raw_commits: list[dict[str, Any]]) -> pl.DataFrame:
    """Aggregates commit counts by date.

    Args:
        raw_commits: A list of raw GitHub commit dictionaries.

    Returns:
        A Polars DataFrame with 'date' and 'commit_count' columns.
    """
    validated_data = _extract_valid_commits(raw_commits)

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


def get_top_committers(
    raw_commits: list[dict[str, Any]], top_n: int = config.default_top_n
) -> pl.DataFrame:
    """Gets top committers with deterministic sorting.

    Args:
        raw_commits: A list of raw GitHub commit dictionaries.
        top_n: The number of top committers to return.

    Returns:
        A Polars DataFrame with 'name' and 'commit_count' columns.
    """
    validated_data = _extract_valid_commits(raw_commits)

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

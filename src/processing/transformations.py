from datetime import datetime
from typing import Any

import polars as pl
from pydantic import ValidationError

from src.domain_models import CommitItem


def _validate_and_flatten(raw_commits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Validates raw commits against CommitItem schema and returns flattened dicts."""
    flattened = []
    for commit_data in raw_commits:
        try:
            date_val = commit_data["date"]
            name_val = commit_data["name"]

            if isinstance(date_val, str) and date_val.endswith("Z"):
                date_val = date_val.replace("Z", "+00:00")
                parsed_date = datetime.fromisoformat(date_val)
            else:
                parsed_date = date_val

            item = CommitItem(date=parsed_date, name=name_val)
            flattened.append({"date": item.date, "name": item.name})
        except KeyError as e:
            model_name = "CommitItem"
            raise ValidationError.from_exception_data(
                model_name, [{"type": "missing", "loc": ("body", e.args[0]), "input": commit_data}]
            ) from e
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

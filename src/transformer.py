from datetime import datetime

import polars as pl

from src.domain_models import CommitRecord


def _records_to_df(records: list[CommitRecord]) -> pl.DataFrame:
    """Convert a list of CommitRecord to a Polars DataFrame with a unified date column."""
    if not records:
        return pl.DataFrame(schema={"sha": pl.String, "author": pl.String, "date": pl.Date})

    # We extract strictly the date part
    data = []
    for r in records:
        d = r.date.date() if isinstance(r.date, datetime) else r.date
        data.append({"sha": r.sha, "author": r.author, "date": d})

    return pl.DataFrame(data, schema={"sha": pl.String, "author": pl.String, "date": pl.Date})


def aggregate_commits_by_date(records: list[CommitRecord]) -> pl.DataFrame:
    """
    Calculate the total number of commits per calendar date.
    Returns a DataFrame with columns: ['date', 'commit_count']
    """
    df = _records_to_df(records)

    if df.is_empty():
        return pl.DataFrame(schema={"date": pl.Date, "commit_count": pl.UInt32})

    return df.group_by("date").len(name="commit_count").sort("date")


def get_top_committers(records: list[CommitRecord]) -> pl.DataFrame:
    """
    Determine the top 5 distinct committers by sheer commit volume.
    Returns a DataFrame with columns: ['author', 'commit_count']
    """
    df = _records_to_df(records)

    if df.is_empty():
        return pl.DataFrame(schema={"author": pl.String, "commit_count": pl.UInt32})

    return (
        df.group_by("author")
        .len(name="commit_count")
        .sort(["commit_count", "author"], descending=[True, False])
        .head(5)
    )

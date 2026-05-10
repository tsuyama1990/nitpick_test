import polars as pl


def commits_to_dataframe(commits: list[dict[str, str | pl.Datetime]]) -> pl.DataFrame:
    """Convert raw commit list to Polars DataFrame with properly parsed dates."""
    if not commits:
        return pl.DataFrame(schema={"date": pl.Date, "author_name": pl.String})

    df = pl.DataFrame(commits)

    # Cast date string to proper datetime, then extract just the Date
    return df.with_columns(
        pl.col("date")
        .str.strptime(pl.Datetime, format="%Y-%m-%dT%H:%M:%SZ")
        .cast(pl.Date)
        .alias("date")
    )


def aggregate_daily_commits(df: pl.DataFrame) -> pl.DataFrame:
    """Aggregate commit count per day."""
    if df.is_empty():
        return pl.DataFrame(schema={"date": pl.Date, "commit_count": pl.UInt32})

    return df.group_by("date").agg(pl.len().alias("commit_count")).sort("date")


def aggregate_top_committers(df: pl.DataFrame, top_n: int = 5) -> pl.DataFrame:
    """Aggregate commit count per committer and return top N."""
    if df.is_empty():
        return pl.DataFrame(schema={"author_name": pl.String, "commit_count": pl.UInt32})

    return (
        df.group_by("author_name")
        .agg(pl.len().alias("commit_count"))
        .sort(["commit_count", "author_name"], descending=[True, False])
        .head(top_n)
    )

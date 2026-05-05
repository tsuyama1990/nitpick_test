import polars as pl

from src.domain_models.github import CommitRecord


def _commits_to_df(commits: list[CommitRecord]) -> pl.DataFrame:
    """Converts a list of CommitRecord objects to a Polars DataFrame."""
    if not all(isinstance(c, CommitRecord) for c in commits):
        msg = "All items must be CommitRecord instances"
        raise TypeError(msg)

    if not commits:
        return pl.DataFrame(
            schema={"date": pl.Datetime, "author_name": pl.Utf8, "message": pl.Utf8}
        )

    data = [
        {
            "date": commit.date.replace(tzinfo=None),  # Remove tz for easier grouping
            "author_name": commit.author_name,
            "message": commit.message,
        }
        for commit in commits
    ]
    return pl.DataFrame(data)


def transform_commits_to_daily_trends(commits: list[CommitRecord]) -> pl.DataFrame:
    """Aggregates commits by date to show daily trends."""
    df = _commits_to_df(commits)
    if df.is_empty():
        return pl.DataFrame(schema={"date": pl.Date, "commit_count": pl.Int64})

    # Cast to Date (removing time) and group
    df = df.with_columns(pl.col("date").cast(pl.Date))

    return df.group_by("date").agg(pl.len().alias("commit_count")).sort("date")


def transform_commits_to_top_committers(
    commits: list[CommitRecord], limit: int = 5
) -> pl.DataFrame:
    """Aggregates commits by author to find the top committers."""
    df = _commits_to_df(commits)
    if df.is_empty():
        return pl.DataFrame(schema={"author_name": pl.Utf8, "commit_count": pl.Int64})

    return (
        df.group_by("author_name")
        .agg(pl.len().alias("commit_count"))
        .sort("commit_count", descending=True)
        .head(limit)
    )

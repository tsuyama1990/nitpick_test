import polars as pl

from src.domain_models.github import CommitInfo


def aggregate_commits_by_date(commits: list[CommitInfo]) -> pl.DataFrame:
    if not commits:
        return pl.DataFrame(schema={"date": pl.Date, "commit_count": pl.Int64})

    # Extract dates
    data = [{"date_str": c.commit.author.date} for c in commits]
    df = pl.DataFrame(data)

    # Cast string to date handling the exact format with time zones
    df_with_date = df.with_columns(
        pl.col("date_str").str.to_datetime("%Y-%m-%dT%H:%M:%SZ").dt.date().alias("date")
    ).drop("date_str")

    # Aggregate
    return df_with_date.group_by("date").agg(pl.len().alias("commit_count")).sort("date")


def aggregate_commits_by_author(commits: list[CommitInfo]) -> pl.DataFrame:
    if not commits:
        return pl.DataFrame(schema={"author": pl.String, "commit_count": pl.Int64})

    # Extract authors
    data = [{"author": c.commit.author.name} for c in commits]
    df = pl.DataFrame(data)

    # Aggregate and get top 5
    return (
        df.group_by("author")
        .agg(pl.len().alias("commit_count"))
        .sort("commit_count", descending=True)
        .head(5)
    )

import polars as pl

from src.domain_models.schemas import CommitItem


def aggregate_commits_by_date(raw_commits: list[dict[str, object]]) -> pl.DataFrame:
    """
    Validates raw commit JSON against the CommitItem schema, extracts the date,
    and returns a Polars DataFrame aggregated by date.
    """
    if not raw_commits:
        return pl.DataFrame(
            {"date": pl.Series(dtype=pl.Date), "commit_count": pl.Series(dtype=pl.UInt32)}
        )

    validated_commits = [CommitItem(**commit) for commit in raw_commits]  # type: ignore[arg-type]
    flat_data = [{"date": c.commit.author.date.date()} for c in validated_commits]
    df = pl.DataFrame(flat_data)

    return (
        df.with_columns(pl.col("date").cast(pl.Date))
        .group_by("date")
        .agg(pl.len().alias("commit_count"))
        .sort("date")
    )


def get_top_committers(raw_commits: list[dict[str, object]], top_n: int = 5) -> pl.DataFrame:
    """
    Validates raw commit JSON, extracts the author name, aggregates to find the
    top committers, and resolves ties alphabetically.
    """
    if not raw_commits:
        return pl.DataFrame(
            {"name": pl.Series(dtype=pl.String), "commit_count": pl.Series(dtype=pl.UInt32)}
        )

    validated_commits = [CommitItem(**commit) for commit in raw_commits]  # type: ignore[arg-type]
    flat_data = [{"name": c.commit.author.name} for c in validated_commits]
    df = pl.DataFrame(flat_data)

    return (
        df.group_by("name")
        .agg(pl.len().alias("commit_count"))
        .sort(["commit_count", "name"], descending=[True, False])
        .head(top_n)
    )

import polars as pl

from src.domain_models.schemas import CommitItem


def aggregate_commits_by_date(raw_commits: list[dict[str, object]]) -> pl.DataFrame:
    """
    Aggregates commits by date. Returns a Polars DataFrame with columns: date, commit_count.
    """
    if not raw_commits:
        schema = {"date": pl.Date, "commit_count": pl.UInt32}
        return pl.DataFrame(schema=schema)

    # Validate and flatten input data
    validated_commits = [CommitItem.model_validate(commit) for commit in raw_commits]

    # Initialize Polars DataFrame
    df = pl.DataFrame([{"date": commit.date, "name": commit.name} for commit in validated_commits])

    # Note that GitHub dates are often ISO strings like "2024-05-17T12:00:00Z".
    # We want just the date. Let's cast to Datetime then Date to be safe, or just string slice.
    # The spec: "extracting the date portion from the datetime string (or object)"
    # We can do df.with_columns(pl.col("date").str.slice(0, 10).cast(pl.Date))

    return (
        df.with_columns(pl.col("date").str.slice(0, 10).cast(pl.Date, strict=False))
        .group_by("date")
        .agg(pl.len().alias("commit_count"))
        .sort("date")
    )


def get_top_committers(raw_commits: list[dict[str, object]], top_n: int = 5) -> pl.DataFrame:
    """
    Gets the top committers. Returns a Polars DataFrame with columns: name, commit_count.
    """
    if not raw_commits:
        schema = {"name": pl.String, "commit_count": pl.UInt32}
        return pl.DataFrame(schema=schema)

    # Validate and flatten input data
    validated_commits = [CommitItem.model_validate(commit) for commit in raw_commits]

    # Initialize Polars DataFrame
    df = pl.DataFrame([{"date": commit.date, "name": commit.name} for commit in validated_commits])

    return (
        df.group_by("name")
        .agg(pl.len().alias("commit_count"))
        .sort(["commit_count", "name"], descending=[True, False])
        .head(top_n)
    )

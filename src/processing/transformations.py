import polars as pl

from src.domain_models.schemas import CommitItem


def aggregate_commits_by_date(raw_commits: list[dict[str, object]]) -> pl.DataFrame:
    """
    Validates a list of dictionaries representing GitHub commits against the CommitItem schema,
    and returns a Polars DataFrame aggregated by date.

    The resulting DataFrame has columns:
        - date: Polars Date type
        - commit_count: Integer representing the number of commits on that date
    """
    if not raw_commits:
        # Return an empty DataFrame with the expected schema
        return pl.DataFrame(
            {"date": [], "commit_count": []}, schema={"date": pl.Date, "commit_count": pl.UInt32}
        )

    # Validate and flatten data
    valid_data = []
    for commit_dict in raw_commits:
        item = CommitItem(**commit_dict)  # type: ignore[arg-type]
        valid_data.append({"date": item.commit.author.date})

    df = pl.DataFrame(valid_data)

    # Cast date, group by, and aggregate
    return (
        df.with_columns(pl.col("date").cast(pl.Date))
        .group_by("date")
        .agg(pl.len().alias("commit_count"))
        .sort("date")
    )


def get_top_committers(raw_commits: list[dict[str, object]], top_n: int = 5) -> pl.DataFrame:
    """
    Validates a list of dictionaries representing GitHub commits against the CommitItem schema,
    and returns a Polars DataFrame of the top committers.

    The resulting DataFrame has columns:
        - name: String, the author's name
        - commit_count: Integer, the number of commits

    Sorting is strictly deterministic: descending by commit_count, then ascending by name.
    """
    if not raw_commits:
        # Return an empty DataFrame with the expected schema
        return pl.DataFrame(
            {"name": [], "commit_count": []}, schema={"name": pl.String, "commit_count": pl.UInt32}
        )

    valid_data = []
    for commit_dict in raw_commits:
        item = CommitItem(**commit_dict)  # type: ignore[arg-type]
        valid_data.append({"name": item.commit.author.name})

    df = pl.DataFrame(valid_data)

    return (
        df.group_by("name")
        .agg(pl.len().alias("commit_count"))
        .sort(["commit_count", "name"], descending=[True, False])
        .head(top_n)
    )

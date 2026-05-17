import polars as pl

from src.domain_models.schemas import CommitItem


def _validate_and_flatten(raw_commits: list[dict[str, object]]) -> list[dict[str, object]]:
    """Validates raw data using Pydantic and returns a flat list for Polars."""
    flattened = []
    for commit in raw_commits:
        # Pydantic validation ensures the payload matches the expected shape
        item = CommitItem(
            name=commit.get("name"),  # type: ignore[arg-type]
            date=commit.get("date")   # type: ignore[arg-type]
        )
        flattened.append({"name": item.name, "date": item.date.date()})
    return flattened


def aggregate_commits_by_date(raw_commits: list[dict[str, object]]) -> pl.DataFrame:
    """Aggregates raw commit payloads by date into a Polars DataFrame."""
    if not raw_commits:
        return pl.DataFrame(schema={"date": pl.Date, "commit_count": pl.UInt32})

    flattened_data = _validate_and_flatten(raw_commits)
    df = pl.DataFrame(flattened_data)

    return (
        df.with_columns(pl.col("date").cast(pl.Date))
        .group_by("date")
        .agg(pl.len().alias("commit_count"))
        .sort("date")
    )


def get_top_committers(raw_commits: list[dict[str, object]], top_n: int = 5) -> pl.DataFrame:
    """Calculates the top N committers with deterministic tie-breaking sorting."""
    if not raw_commits:
        return pl.DataFrame(schema={"name": pl.String, "commit_count": pl.UInt32})

    flattened_data = _validate_and_flatten(raw_commits)
    df = pl.DataFrame(flattened_data)

    return (
        df.group_by("name")
        .agg(pl.len().alias("commit_count"))
        .sort(["commit_count", "name"], descending=[True, False])
        .head(top_n)
    )

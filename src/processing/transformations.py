import polars as pl

from src.domain_models.schemas import CommitItem


def aggregate_commits_by_date(raw_commits: list[dict[str, object]]) -> pl.DataFrame:
    """
    Validates commit data and aggregates the commit count by date.

    Args:
        raw_commits: A list of dictionaries representing the API output.
    Returns:
        A Polars DataFrame containing 'date' and 'commit_count'.
    """
    # 1. Validate data
    validated_data = []
    for raw_item in raw_commits:
        # Pydantic validation (explicit dictionary unpacking with ignore type to prevent Mypy issue)
        item = CommitItem(**raw_item)  # type: ignore[arg-type]
        validated_data.append({"date": item.date.date()})

    # 2. Create DataFrame
    # If list is empty, initialize with explicit schema
    if not validated_data:
        df = pl.DataFrame(schema={"date": pl.Date})
        return df.with_columns(pl.lit(0).cast(pl.UInt32).alias("commit_count"))

    df = pl.DataFrame(validated_data)

    # 3. Aggregate
    # Cast "date" to Date explicitly if not already
    df = df.with_columns(pl.col("date").cast(pl.Date))

    return df.group_by("date").agg(pl.len().alias("commit_count")).sort("date")


def get_top_committers(raw_commits: list[dict[str, object]], top_n: int = 5) -> pl.DataFrame:
    """
    Validates commit data and gets top committers sorted by commit count descending, then name ascending.

    Args:
        raw_commits: A list of dictionaries representing the API output.
        top_n: Number of top committers to return.
    Returns:
        A Polars DataFrame containing 'name' and 'commit_count'.
    """
    # 1. Validate data
    validated_data = []
    for raw_item in raw_commits:
        item = CommitItem(**raw_item)  # type: ignore[arg-type]
        validated_data.append({"name": item.name})

    # 2. Create DataFrame
    if not validated_data:
        df = pl.DataFrame(schema={"name": pl.String})
        return df.with_columns(pl.lit(0).cast(pl.UInt32).alias("commit_count"))

    df = pl.DataFrame(validated_data)

    # 3. Aggregate
    df_agg = df.group_by("name").agg(pl.len().alias("commit_count"))

    # 4. Sort and limit
    # Secondary stable sort: descending by commit_count, ascending by name
    return df_agg.sort(["commit_count", "name"], descending=[True, False]).head(top_n)

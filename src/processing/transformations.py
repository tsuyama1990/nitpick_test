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

    from collections.abc import Iterator

    # Validate and flatten data into an iterator
    def iterate_valid_commits() -> Iterator[dict[str, object]]:
        for commit_dict in raw_commits:
            item = CommitItem(**commit_dict)  # type: ignore[arg-type]
            yield {"date": item.commit.author.date}

    # Process the iterator in chunks to avoid OOM
    schema = {"date": pl.Datetime}
    lf = pl.LazyFrame({"date": []}, schema=schema)

    chunk_size = 1000
    current_chunk = []

    for item in iterate_valid_commits():
        current_chunk.append(item)
        if len(current_chunk) >= chunk_size:
            chunk_lf = pl.LazyFrame(current_chunk, schema=schema)
            lf = pl.concat([lf, chunk_lf])
            current_chunk = []

    if current_chunk:
        chunk_lf = pl.LazyFrame(current_chunk, schema=schema)
        lf = pl.concat([lf, chunk_lf])

    # Cast date, group by, and aggregate
    return (
        lf.with_columns(pl.col("date").cast(pl.Date))
        .group_by("date")
        .agg(pl.len().alias("commit_count"))
        .sort("date")
        .collect()
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

    from collections.abc import Iterator

    # Validate and flatten data into an iterator
    def iterate_valid_committers() -> Iterator[dict[str, object]]:
        for commit_dict in raw_commits:
            item = CommitItem(**commit_dict)  # type: ignore[arg-type]
            yield {"name": item.commit.author.name}

    # Process the iterator in chunks to avoid OOM
    schema = {"name": pl.String}
    lf = pl.LazyFrame({"name": []}, schema=schema)

    chunk_size = 1000
    current_chunk = []

    for item in iterate_valid_committers():
        current_chunk.append(item)
        if len(current_chunk) >= chunk_size:
            chunk_lf = pl.LazyFrame(current_chunk, schema=schema)
            lf = pl.concat([lf, chunk_lf])
            current_chunk = []

    if current_chunk:
        chunk_lf = pl.LazyFrame(current_chunk, schema=schema)
        lf = pl.concat([lf, chunk_lf])

    return (
        lf.group_by("name")
        .agg(pl.len().alias("commit_count"))
        .sort(["commit_count", "name"], descending=[True, False])
        .head(top_n)
        .collect()
    )

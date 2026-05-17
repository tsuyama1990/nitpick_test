import polars as pl

from src.domain_models.schemas import CommitAuthor, CommitData, CommitItem


def _validate_and_flatten_commits(raw_commits: list[dict[str, object]]) -> list[dict[str, object]]:
    """
    Validates a list of raw commit dictionaries against the Pydantic schema
    and flattens the resulting structure into a simpler list of dictionaries
    optimized for Polars DataFrame initialization.

    Args:
        raw_commits: List of raw JSON commit payloads from the GitHub API.

    Returns:
        List of flattened dictionaries containing only 'name' (str) and 'date' (datetime.date).
    """
    flattened_data: list[dict[str, object]] = []

    for raw_item in raw_commits:
        # Safely extract nested dictionaries to satisfy static type checkers without forcing casts
        raw_commit = raw_item.get("commit", {})
        raw_commit_dict = dict(raw_commit) if isinstance(raw_commit, dict) else {}
        raw_author = raw_commit_dict.get("author", {})
        raw_author_dict = dict(raw_author) if isinstance(raw_author, dict) else {}

        # Instantiate Pydantic models with explicit field mapping.
        # This bypasses dictionary unpacking errors while maintaining strict `extra="forbid"` schema validation.
        author = CommitAuthor(
            name=str(raw_author_dict.get("name", "")),
            date=raw_author_dict.get("date"),  # type: ignore[arg-type]
        )
        commit_data = CommitData(author=author)
        item = CommitItem(commit=commit_data)

        flattened_data.append(
            {
                "name": item.commit.author.name,
                "date": item.commit.author.date.date(),
            }
        )

    return flattened_data


def aggregate_commits_by_date(raw_commits: list[dict[str, object]]) -> pl.DataFrame:
    """
    Aggregates raw commit data into a Polars DataFrame grouped by date.

    Args:
        raw_commits: List of raw JSON commit payloads.

    Returns:
        A Polars DataFrame with columns `date` (pl.Date) and `commit_count` (pl.UInt32).
    """
    if not raw_commits:
        return pl.DataFrame(schema={"date": pl.Date, "commit_count": pl.UInt32})

    flattened = _validate_and_flatten_commits(raw_commits)
    df = pl.DataFrame(flattened)

    return (
        df.with_columns(pl.col("date").cast(pl.Date))
        .group_by("date")
        .agg(pl.len().alias("commit_count"))
        .sort("date")
    )


def get_top_committers(raw_commits: list[dict[str, object]], top_n: int = 5) -> pl.DataFrame:
    """
    Calculates the top committers from the raw commit data.
    Uses a secondary stable sort (ascending by name) to ensure deterministic tie-breaking.

    Args:
        raw_commits: List of raw JSON commit payloads.
        top_n: The maximum number of top committers to return.

    Returns:
        A Polars DataFrame with columns `name` (pl.String) and `commit_count` (pl.UInt32).
    """
    if not raw_commits:
        return pl.DataFrame(schema={"name": pl.String, "commit_count": pl.UInt32})

    flattened = _validate_and_flatten_commits(raw_commits)
    df = pl.DataFrame(flattened)

    return (
        df.with_columns(pl.col("name").cast(pl.String))
        .group_by("name")
        .agg(pl.len().alias("commit_count"))
        .sort(["commit_count", "name"], descending=[True, False])
        .head(top_n)
    )

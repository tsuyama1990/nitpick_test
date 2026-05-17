import polars as pl

from src.domain_models.schemas import CommitAuthor, CommitData, CommitItem


def _validate_and_flatten_commits(raw_commits: list[dict[str, object]]) -> list[dict[str, object]]:
    """Helper to validate raw commits explicitly and flatten for Polars."""
    flattened_data: list[dict[str, object]] = []
    for raw_item in raw_commits:
        # Explicitly map keys to bypass strict unpacking issues and raise clean ValidationErrors
        raw_commit = raw_item.get("commit", {})
        raw_commit_dict = dict(raw_commit) if isinstance(raw_commit, dict) else {}
        raw_author = raw_commit_dict.get("author", {})
        raw_author_dict = dict(raw_author) if isinstance(raw_author, dict) else {}

        # Pydantic validation (will raise ValidationError if malformed, Pydantic natively parses dates)
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

import polars as pl
from pydantic import ValidationError

from src.domain_models.schemas import CommitItem


def _parse_commit_item(rc: object) -> CommitItem:
    """Helper to parse a raw commit item with strict schema enforcement."""
    if not isinstance(rc, dict) or "commit" not in rc or not isinstance(rc["commit"], dict):
        err_msg = "Validation error"
        raise ValidationError.from_exception_data(err_msg, [])

    commit_dict = rc["commit"]
    if "author" not in commit_dict or not isinstance(commit_dict["author"], dict):
        err_msg = "Validation error"
        raise ValidationError.from_exception_data(err_msg, [])

    author_dict = commit_dict["author"]

    extracted_rc = {
        "commit": {"author": {"name": author_dict.get("name"), "date": author_dict.get("date")}}
    }
    return CommitItem(**extracted_rc)  # type: ignore[arg-type]


def aggregate_commits_by_date(raw_commits: list[dict[str, object]]) -> pl.DataFrame:
    """Aggregates commits by date."""
    valid_data = []
    for rc in raw_commits:
        try:
            item = _parse_commit_item(rc)
            valid_data.append({"date": item.commit.author.date.date()})
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            err_msg = "Validation error"
            raise ValidationError.from_exception_data(err_msg, []) from e

    if not valid_data:
        return pl.DataFrame(schema={"date": pl.Date, "commit_count": pl.UInt32})

    df = pl.DataFrame(valid_data)

    return (
        df.with_columns(pl.col("date").cast(pl.Date))
        .group_by("date")
        .agg(pl.len().alias("commit_count"))
        .sort("date")
    )


def get_top_committers(raw_commits: list[dict[str, object]], top_n: int = 5) -> pl.DataFrame:
    """Gets top committers."""
    valid_data = []
    for rc in raw_commits:
        try:
            item = _parse_commit_item(rc)
            valid_data.append({"name": item.commit.author.name})
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            err_msg = "Validation error"
            raise ValidationError.from_exception_data(err_msg, []) from e

    if not valid_data:
        return pl.DataFrame(schema={"name": pl.Utf8, "commit_count": pl.UInt32})

    df = pl.DataFrame(valid_data)

    return (
        df.group_by("name")
        .agg(pl.len().alias("commit_count"))
        .sort(["commit_count", "name"], descending=[True, False])
        .head(top_n)
    )

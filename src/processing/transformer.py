import polars as pl

from src.domain_models import CommitRecord


def _records_to_df(records: list[CommitRecord]) -> pl.DataFrame:
    # Convert dates to string (YYYY-MM-DD) for aggregation
    data = [
        {
            "commit_hash": r.commit_hash,
            "author": r.author,
            "date": r.date.strftime("%Y-%m-%d"),
        }
        for r in records
    ]
    return pl.DataFrame(data, schema={"commit_hash": pl.Utf8, "author": pl.Utf8, "date": pl.Utf8})


def calculate_daily_commits(records: list[CommitRecord]) -> pl.DataFrame:
    if not records:
        return pl.DataFrame(
            {"date": [], "commit_count": []}, schema={"date": pl.Utf8, "commit_count": pl.UInt32}
        )

    df = _records_to_df(records)
    return df.group_by("date").len(name="commit_count").sort("date")


def get_top_committers(records: list[CommitRecord]) -> pl.DataFrame:
    if not records:
        return pl.DataFrame(
            {"author": [], "commit_count": []},
            schema={"author": pl.Utf8, "commit_count": pl.UInt32},
        )

    df = _records_to_df(records)
    return (
        df.group_by("author")
        .len(name="commit_count")
        .sort(by=["commit_count", "author"], descending=[True, False])
        .head(5)
    )

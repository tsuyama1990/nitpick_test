import polars as pl

from src.domain_models import CommitRecord


def _records_to_df(records: list[CommitRecord]) -> pl.DataFrame:
    if not records:
        return pl.DataFrame(
            {"commit_hash": [], "author": [], "date": []},
            schema={"commit_hash": pl.Utf8, "author": pl.Utf8, "date": pl.Utf8},
        )

    # Construct DataFrame and use vectorized date extraction to pure string
    df = pl.DataFrame(
        {
            "commit_hash": [r.commit_hash for r in records],
            "author": [r.author for r in records],
            "date": [r.date for r in records],
        }
    )
    return df.with_columns(pl.col("date").dt.strftime("%Y-%m-%d").alias("date"))


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

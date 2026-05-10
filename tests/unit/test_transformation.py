from datetime import date

import polars as pl

from src.transformation.metrics import (
    aggregate_daily_commits,
    aggregate_top_committers,
    commits_to_dataframe,
)


def test_commits_to_dataframe() -> None:
    commits = [
        {"date": "2023-10-01T12:00:00Z", "author_name": "Alice"},
        {"date": "2023-10-01T14:00:00Z", "author_name": "Bob"},
        {"date": "2023-10-02T10:00:00Z", "author_name": "Alice"},
    ]

    df = commits_to_dataframe(commits) # type: ignore[arg-type]

    assert isinstance(df, pl.DataFrame)
    assert len(df) == 3
    assert df.schema["date"] == pl.Date

    # Check first row date is correctly parsed to Date object
    assert df["date"][0] == date(2023, 10, 1)

def test_aggregate_daily_commits() -> None:
    # Setup dataframe with 2 commits on the 1st, 1 on the 2nd
    df = pl.DataFrame({
        "date": [date(2023, 10, 1), date(2023, 10, 1), date(2023, 10, 2)],
        "author_name": ["Alice", "Bob", "Alice"]
    }, schema={"date": pl.Date, "author_name": pl.String})

    daily = aggregate_daily_commits(df)

    assert len(daily) == 2

    first_day = daily.filter(pl.col("date") == date(2023, 10, 1))
    assert first_day["commit_count"][0] == 2

    second_day = daily.filter(pl.col("date") == date(2023, 10, 2))
    assert second_day["commit_count"][0] == 1

def test_aggregate_top_committers() -> None:
    df = pl.DataFrame({
        "date": [date(2023, 10, 1)] * 6,
        "author_name": ["Alice", "Alice", "Alice", "Bob", "Bob", "Charlie"]
    }, schema={"date": pl.Date, "author_name": pl.String})

    top = aggregate_top_committers(df, top_n=2)

    assert len(top) == 2
    assert top["author_name"][0] == "Alice"
    assert top["commit_count"][0] == 3
    assert top["author_name"][1] == "Bob"
    assert top["commit_count"][1] == 2

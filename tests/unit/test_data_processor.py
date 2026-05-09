import polars as pl
import pytest

from src.transformation.data_processor import DataProcessor
from src.transformation.exceptions import TransformationError


def test_commits_per_day_empty() -> None:
    df = pl.DataFrame({"author_date": []}, schema={"author_date": pl.Utf8})
    result = DataProcessor.commits_per_day(df)
    assert result.is_empty()
    assert result.schema == {"date": pl.Date, "commits": pl.UInt32}


def test_commits_per_day_valid() -> None:
    df = pl.DataFrame(
        {
            "author_date": [
                "2023-10-01T10:00:00Z",
                "2023-10-01T12:00:00Z",
                "2023-10-02T10:00:00Z",
            ]
        }
    )
    result = DataProcessor.commits_per_day(df)
    from datetime import date

    expected = pl.DataFrame(
        {
            "date": [date(2023, 10, 1), date(2023, 10, 2)],
            "commits": [2, 1],
        },
        schema={"date": pl.Date, "commits": pl.UInt32},
    )
    assert result.equals(expected)


def test_top_committers_empty() -> None:
    df = pl.DataFrame({"author_name": []}, schema={"author_name": pl.Utf8})
    result = DataProcessor.top_committers(df)
    assert result.is_empty()
    assert result.schema == {"author_name": pl.Utf8, "commits": pl.UInt32}


def test_top_committers_valid() -> None:
    df = pl.DataFrame(
        {"author_name": ["Alice", "Bob", "Alice", "Charlie", "Alice", "David", "Eve", "Frank"]}
    )
    result = DataProcessor.top_committers(df, limit=2)
    # Actually the order of Bob/Charlie/David/Eve/Frank might be non-deterministic if they all have 1 commit,
    # but Alice is definitely first. Let's just check limit=1 for exactness, or check Alice.
    assert result.row(0) == ("Alice", 3)
    assert len(result) == 2


def test_commits_per_day_missing_column() -> None:
    df = pl.DataFrame({"wrong_col": ["a", "b"]})
    with pytest.raises(TransformationError, match="Missing required column: author_date"):
        DataProcessor.commits_per_day(df)


def test_top_committers_missing_column() -> None:
    df = pl.DataFrame({"wrong_col": ["a", "b"]})
    with pytest.raises(TransformationError, match="Missing required column: author_name"):
        DataProcessor.top_committers(df)

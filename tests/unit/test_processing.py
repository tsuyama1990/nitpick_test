import datetime

import polars as pl
import pytest
from pydantic import ValidationError

from src.processing.transformations import aggregate_commits_by_date, get_top_committers


def test_aggregate_commits_by_date_valid_data() -> None:
    """Test date aggregation with a valid dataset."""
    raw_commits = [
        {"name": "Alice", "date": "2023-10-01T10:00:00Z"},
        {"name": "Alice", "date": "2023-10-01T14:00:00Z"},
        {"name": "Bob", "date": "2023-10-01T15:00:00Z"},
        {"name": "Charlie", "date": "2023-10-02T10:00:00Z"},
        {"name": "Alice", "date": "2023-10-02T11:00:00Z"},
        {"name": "Dave", "date": "2023-10-02T12:00:00Z"},
        {"name": "Bob", "date": "2023-10-02T13:00:00Z"},
        {"name": "Charlie", "date": "2023-10-03T09:00:00Z"},
        {"name": "Alice", "date": "2023-10-03T10:00:00Z"},
        {"name": "Dave", "date": "2023-10-03T11:00:00Z"},
    ]

    df = aggregate_commits_by_date(raw_commits)  # type: ignore[arg-type]

    # Assert schema
    assert df.schema["date"] == pl.Date
    assert df.schema["commit_count"] == pl.UInt32

    # Assert values
    results = df.to_dicts()
    assert len(results) == 3
    assert results[0] == {"date": datetime.date(2023, 10, 1), "commit_count": 3}
    assert results[1] == {"date": datetime.date(2023, 10, 2), "commit_count": 4}
    assert results[2] == {"date": datetime.date(2023, 10, 3), "commit_count": 3}


def test_get_top_committers_valid_data() -> None:
    """Test committer aggregation with ties for deterministic sorting."""
    raw_commits = [
        {"name": "Bob", "date": "2023-10-01T10:00:00Z"},
        {"name": "Bob", "date": "2023-10-01T14:00:00Z"},
        {"name": "Charlie", "date": "2023-10-01T15:00:00Z"},
        {"name": "Charlie", "date": "2023-10-02T10:00:00Z"},
        {"name": "Alice", "date": "2023-10-02T11:00:00Z"},
        {"name": "Alice", "date": "2023-10-02T12:00:00Z"},
        {"name": "Dave", "date": "2023-10-02T13:00:00Z"},
    ]

    # Alice, Bob, Charlie all have 2 commits. Dave has 1.
    df = get_top_committers(raw_commits, top_n=2)  # type: ignore[arg-type]

    assert df.schema["name"] == pl.String
    assert df.schema["commit_count"] == pl.UInt32

    results = df.to_dicts()
    assert len(results) == 2
    # Secondary sort is alphabetical ascending (A, B, C)
    assert results[0] == {"name": "Alice", "commit_count": 2}
    assert results[1] == {"name": "Bob", "commit_count": 2}


def test_empty_datasets() -> None:
    """Test aggregation functions with an empty dataset."""
    df_date = aggregate_commits_by_date([])
    assert df_date.schema["date"] == pl.Date
    assert df_date.schema["commit_count"] == pl.UInt32
    assert df_date.height == 0

    df_committer = get_top_committers([])
    assert df_committer.schema["name"] == pl.String
    assert df_committer.schema["commit_count"] == pl.UInt32
    assert df_committer.height == 0


def test_pydantic_validation_error() -> None:
    """Test that malformed input raises a ValidationError."""
    raw_commits = [
        {"name": "Alice"},  # Missing date
    ]

    with pytest.raises(ValidationError):
        aggregate_commits_by_date(raw_commits)  # type: ignore[arg-type]

    with pytest.raises(ValidationError):
        get_top_committers(raw_commits)  # type: ignore[arg-type]


def test_pydantic_validation_extra_forbid() -> None:
    """Test that extra fields raise a ValidationError."""
    raw_commits = [
        {"name": "Alice", "date": "2023-10-01T10:00:00Z", "extra_field": "bad"},
    ]

    with pytest.raises(ValidationError):
        aggregate_commits_by_date(raw_commits)  # type: ignore[arg-type]

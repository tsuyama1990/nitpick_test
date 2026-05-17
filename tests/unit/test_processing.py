from datetime import UTC
from typing import Any

import polars as pl
import pytest
from pydantic import ValidationError

from src.processing.transformations import aggregate_commits_by_date, get_top_committers


def test_aggregate_commits_by_date_valid() -> None:
    data: list[dict[str, Any]] = [
        {"date": "2023-10-01T10:00:00Z", "name": "Alice"},
        {"date": "2023-10-01T12:00:00Z", "name": "Bob"},
        {"date": "2023-10-02T10:00:00Z", "name": "Alice"},
        {"date": "2023-10-03T10:00:00Z", "name": "Charlie"},
    ]
    df = aggregate_commits_by_date(data)

    assert df.schema == {"date": pl.Date, "commit_count": pl.UInt32}
    assert len(df) == 3

    results = df.to_dicts()
    assert results[0]["commit_count"] == 2  # 2023-10-01
    assert results[1]["commit_count"] == 1  # 2023-10-02
    assert results[2]["commit_count"] == 1  # 2023-10-03


def test_aggregate_commits_by_date_empty() -> None:
    df = aggregate_commits_by_date([])
    assert df.schema == {"date": pl.Date, "commit_count": pl.UInt32}
    assert len(df) == 0


def test_get_top_committers_valid() -> None:
    data: list[dict[str, Any]] = [
        {"date": "2023-10-01T10:00:00Z", "name": "Alice"},
        {"date": "2023-10-01T12:00:00Z", "name": "Bob"},
        {"date": "2023-10-02T10:00:00Z", "name": "Alice"},
        {"date": "2023-10-03T10:00:00Z", "name": "Charlie"},
    ]
    df = get_top_committers(data, top_n=2)

    assert df.schema == {"name": pl.Utf8, "commit_count": pl.UInt32}
    assert len(df) == 2

    results = df.to_dicts()
    assert results[0]["name"] == "Alice"
    assert results[0]["commit_count"] == 2
    assert results[1]["name"] == "Bob"
    assert results[1]["commit_count"] == 1


def test_get_top_committers_tie_breaker() -> None:
    # Charlie, Bob, and Alice all have 2 commits.
    # Sorted by count (desc) then name (asc), top 2 should be Alice and Bob.
    data: list[dict[str, Any]] = [
        {"date": "2023-10-01T10:00:00Z", "name": "Charlie"},
        {"date": "2023-10-01T11:00:00Z", "name": "Bob"},
        {"date": "2023-10-01T12:00:00Z", "name": "Alice"},
        {"date": "2023-10-02T10:00:00Z", "name": "Charlie"},
        {"date": "2023-10-02T11:00:00Z", "name": "Bob"},
        {"date": "2023-10-02T12:00:00Z", "name": "Alice"},
    ]
    df = get_top_committers(data, top_n=2)

    results = df.to_dicts()
    assert len(results) == 2
    assert results[0]["name"] == "Alice"
    assert results[1]["name"] == "Bob"


def test_get_top_committers_empty() -> None:
    df = get_top_committers([])
    assert df.schema == {"name": pl.Utf8, "commit_count": pl.UInt32}
    assert len(df) == 0


def test_pydantic_validation_error() -> None:
    data: list[dict[str, Any]] = [{"name": "Alice"}]  # Missing date
    with pytest.raises(ValidationError):
        aggregate_commits_by_date(data)
    with pytest.raises(ValidationError):
        get_top_committers(data)


def test_pydantic_validation_error_date_not_str() -> None:
    from datetime import datetime

    # Test fallback flow where date is already a datetime
    data: list[dict[str, Any]] = [{"date": datetime(2023, 10, 1, tzinfo=UTC), "name": "Alice"}]
    df = aggregate_commits_by_date(data)
    assert len(df) == 1

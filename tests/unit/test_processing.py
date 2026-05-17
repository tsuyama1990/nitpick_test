import polars as pl
import pytest
from pydantic import ValidationError

from src.processing.transformations import aggregate_commits_by_date, get_top_committers


def test_aggregate_commits_by_date_valid() -> None:
    # 10 commits spread across 3 different days by 4 different authors
    raw_commits: list[dict[str, object]] = [
        {"commit": {"author": {"date": "2024-05-17T12:00:00Z", "name": "Alice"}}},
        {"commit": {"author": {"date": "2024-05-17T13:00:00Z", "name": "Bob"}}},
        {"commit": {"author": {"date": "2024-05-17T14:00:00Z", "name": "Charlie"}}},
        {"commit": {"author": {"date": "2024-05-18T10:00:00Z", "name": "Alice"}}},
        {"commit": {"author": {"date": "2024-05-18T11:00:00Z", "name": "David"}}},
        {"commit": {"author": {"date": "2024-05-18T12:00:00Z", "name": "Bob"}}},
        {"commit": {"author": {"date": "2024-05-18T13:00:00Z", "name": "Charlie"}}},
        {"commit": {"author": {"date": "2024-05-19T09:00:00Z", "name": "Alice"}}},
        {"commit": {"author": {"date": "2024-05-19T10:00:00Z", "name": "Bob"}}},
        {"commit": {"author": {"date": "2024-05-19T11:00:00Z", "name": "David"}}},
    ]

    df = aggregate_commits_by_date(raw_commits)

    assert isinstance(df, pl.DataFrame)
    assert df.schema["date"] == pl.Date
    assert df.schema["commit_count"] == pl.UInt32

    # Check the aggregated counts
    results = df.to_dicts()
    assert len(results) == 3

    # 2024-05-17: 3 commits
    assert str(results[0]["date"]) == "2024-05-17"
    assert results[0]["commit_count"] == 3

    # 2024-05-18: 4 commits
    assert str(results[1]["date"]) == "2024-05-18"
    assert results[1]["commit_count"] == 4

    # 2024-05-19: 3 commits
    assert str(results[2]["date"]) == "2024-05-19"
    assert results[2]["commit_count"] == 3


def test_aggregate_commits_by_date_empty() -> None:
    df = aggregate_commits_by_date([])
    assert isinstance(df, pl.DataFrame)
    assert df.is_empty()
    assert df.schema["date"] == pl.Date
    assert df.schema["commit_count"] == pl.UInt32


def test_get_top_committers_valid() -> None:
    # 3 authors all have exactly 2 commits
    raw_commits: list[dict[str, object]] = [
        {"commit": {"author": {"date": "2024-05-17T12:00:00Z", "name": "Charlie"}}},
        {"commit": {"author": {"date": "2024-05-18T12:00:00Z", "name": "Charlie"}}},
        {"commit": {"author": {"date": "2024-05-17T13:00:00Z", "name": "Bob"}}},
        {"commit": {"author": {"date": "2024-05-18T13:00:00Z", "name": "Bob"}}},
        {"commit": {"author": {"date": "2024-05-17T14:00:00Z", "name": "Alice"}}},
        {"commit": {"author": {"date": "2024-05-18T14:00:00Z", "name": "Alice"}}},
    ]

    df = get_top_committers(raw_commits, top_n=2)

    assert isinstance(df, pl.DataFrame)
    assert df.schema["name"] == pl.String
    assert df.schema["commit_count"] == pl.UInt32

    results = df.to_dicts()
    assert len(results) == 2

    # Due to deterministic sorting (descending by count, ascending by name)
    # Alice, Bob, Charlie all have 2 commits. So Alice and Bob should be top 2.
    assert results[0]["name"] == "Alice"
    assert results[0]["commit_count"] == 2
    assert results[1]["name"] == "Bob"
    assert results[1]["commit_count"] == 2


def test_get_top_committers_empty() -> None:
    df = get_top_committers([])
    assert isinstance(df, pl.DataFrame)
    assert df.is_empty()
    assert df.schema["name"] == pl.String
    assert df.schema["commit_count"] == pl.UInt32


def test_pydantic_validation_integration() -> None:
    # missing the author date field
    malformed_commits: list[dict[str, object]] = [
        {"commit": {"author": {"name": "Alice"}}},
    ]

    with pytest.raises(ValidationError):
        aggregate_commits_by_date(malformed_commits)

    with pytest.raises(ValidationError):
        get_top_committers(malformed_commits)

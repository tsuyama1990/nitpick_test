from datetime import date
from typing import Any

import polars as pl
import pytest
from pydantic import ValidationError

from src.processing.transformations import aggregate_commits_by_date, get_top_committers


def test_aggregate_commits_by_date_valid() -> None:
    raw_commits: list[dict[str, Any]] = [
        {"commit": {"author": {"name": "Alice", "date": "2023-10-01T10:00:00Z"}}},
        {"commit": {"author": {"name": "Bob", "date": "2023-10-01T11:00:00Z"}}},
        {"commit": {"author": {"name": "Alice", "date": "2023-10-02T10:00:00Z"}}},
        {"commit": {"author": {"name": "Charlie", "date": "2023-10-03T10:00:00Z"}}},
    ]

    df = aggregate_commits_by_date(raw_commits)

    assert df.schema["date"] == pl.Date
    assert isinstance(df.schema["commit_count"], pl.DataType)

    res = df.to_dicts()
    assert res == [
        {"date": date(2023, 10, 1), "commit_count": 2},
        {"date": date(2023, 10, 2), "commit_count": 1},
        {"date": date(2023, 10, 3), "commit_count": 1},
    ]


def test_aggregate_commits_by_date_empty() -> None:
    df = aggregate_commits_by_date([])
    assert df.schema["date"] == pl.Date
    assert len(df) == 0


def test_get_top_committers_valid() -> None:
    raw_commits: list[dict[str, Any]] = [
        {"commit": {"author": {"name": "Bob", "date": "2023-10-01T10:00:00Z"}}},
        {"commit": {"author": {"name": "Bob", "date": "2023-10-01T11:00:00Z"}}},
        {"commit": {"author": {"name": "Alice", "date": "2023-10-02T10:00:00Z"}}},
        {"commit": {"author": {"name": "Alice", "date": "2023-10-03T10:00:00Z"}}},
        {"commit": {"author": {"name": "Charlie", "date": "2023-10-03T10:00:00Z"}}},
        {"commit": {"author": {"name": "Charlie", "date": "2023-10-03T11:00:00Z"}}},
    ]
    # Everyone has 2 commits. Tiebreak is by name.
    # Alice -> Bob -> Charlie
    df = get_top_committers(raw_commits, top_n=2)
    assert len(df) == 2
    res = df.to_dicts()
    assert res == [
        {"name": "Alice", "commit_count": 2},
        {"name": "Bob", "commit_count": 2},
    ]


def test_get_top_committers_empty() -> None:
    df = get_top_committers([])
    assert len(df) == 0
    assert df.schema["name"] == pl.String


def test_transformations_pydantic_validation() -> None:
    malformed: list[dict[str, Any]] = [
        {"commit": {"author": {"name": "Alice"}}}  # missing date
    ]

    with pytest.raises(ValidationError):
        aggregate_commits_by_date(malformed)

    with pytest.raises(ValidationError):
        get_top_committers(malformed)

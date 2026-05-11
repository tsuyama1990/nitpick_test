import datetime
from typing import Any

import polars as pl
import pytest
from pydantic import ValidationError

from src.processing.transformations import aggregate_commits_by_date, get_top_committers


def get_mock_commits() -> list[dict[str, Any]]:
    # 10 commits, 3 days, 4 authors
    return [
        {"commit": {"author": {"name": "Alice", "date": "2024-01-01T10:00:00Z"}}},
        {"commit": {"author": {"name": "Alice", "date": "2024-01-01T12:00:00Z"}}},
        {"commit": {"author": {"name": "Bob", "date": "2024-01-01T15:00:00Z"}}},
        {"commit": {"author": {"name": "Bob", "date": "2024-01-02T09:00:00Z"}}},
        {"commit": {"author": {"name": "Charlie", "date": "2024-01-02T11:00:00Z"}}},
        {"commit": {"author": {"name": "Charlie", "date": "2024-01-02T14:00:00Z"}}},
        {"commit": {"author": {"name": "Dave", "date": "2024-01-03T10:00:00Z"}}},
        {"commit": {"author": {"name": "Dave", "date": "2024-01-03T13:00:00Z"}}},
        {"commit": {"author": {"name": "Alice", "date": "2024-01-03T16:00:00Z"}}},
        {"commit": {"author": {"name": "Bob", "date": "2024-01-03T18:00:00Z"}}},
    ]


def test_aggregate_commits_by_date_valid() -> None:
    raw_commits = get_mock_commits()
    df = aggregate_commits_by_date(raw_commits)

    assert df.schema["date"] == pl.Date
    assert df.schema["commit_count"] in (pl.UInt32, pl.Int64, pl.Int32)

    # 2024-01-01: 3
    # 2024-01-02: 3
    # 2024-01-03: 4
    counts = dict(zip(df["date"].to_list(), df["commit_count"].to_list(), strict=False))

    assert counts[datetime.date(2024, 1, 1)] == 3
    assert counts[datetime.date(2024, 1, 2)] == 3
    assert counts[datetime.date(2024, 1, 3)] == 4
    assert df.height == 3
    assert df["commit_count"].sum() == 10


def test_get_top_committers_deterministic() -> None:
    raw_commits = get_mock_commits()
    df = get_top_committers(raw_commits, top_n=2)

    assert df.schema["name"] == pl.String
    assert df.schema["commit_count"] in (pl.UInt32, pl.Int64, pl.Int32)

    # Authors: Alice (3), Bob (3), Charlie (2), Dave (2)
    # top 2, Alice and Bob should be returned. Since counts are equal (3), deterministic sorting
    res = df.to_dicts()
    assert len(res) == 2
    assert res[0]["name"] == "Alice"
    assert res[0]["commit_count"] == 3
    assert res[1]["name"] == "Bob"
    assert res[1]["commit_count"] == 3


def test_empty_dataset() -> None:
    df_date = aggregate_commits_by_date([])
    assert df_date.height == 0
    assert df_date.schema["date"] == pl.Date

    df_authors = get_top_committers([])
    assert df_authors.height == 0
    assert df_authors.schema["name"] == pl.String


def test_pydantic_validation_integration() -> None:
    malformed: list[dict[str, Any]] = [{"commit": {"author": {"name": "Alice"}}}]
    with pytest.raises(ValidationError):
        aggregate_commits_by_date(malformed)

    with pytest.raises(ValidationError):
        get_top_committers(malformed)

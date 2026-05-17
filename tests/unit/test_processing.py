import datetime

import polars as pl
import pytest
from pydantic import ValidationError

from src.processing.transformations import aggregate_commits_by_date, get_top_committers


def test_aggregate_commits_by_date_valid() -> None:
    raw_commits: list[dict[str, object]] = [
        {"commit": {"author": {"name": "Alice", "date": "2023-10-27T10:00:00Z"}}},
        {"commit": {"author": {"name": "Bob", "date": "2023-10-27T11:00:00Z"}}},
        {"commit": {"author": {"name": "Alice", "date": "2023-10-28T10:00:00Z"}}},
    ]
    df = aggregate_commits_by_date(raw_commits)
    assert df.shape == (2, 2)
    assert df.columns == ["date", "commit_count"]
    assert df.dtypes == [pl.Date, pl.UInt32]

    # Check values
    results = df.to_dicts()
    assert results[0] == {"date": datetime.date(2023, 10, 27), "commit_count": 2}
    assert results[1] == {"date": datetime.date(2023, 10, 28), "commit_count": 1}


def test_aggregate_commits_by_date_empty() -> None:
    raw_commits: list[dict[str, object]] = []
    df = aggregate_commits_by_date(raw_commits)
    assert df.shape == (0, 2)
    assert df.columns == ["date", "commit_count"]
    assert df.dtypes == [pl.Date, pl.UInt32]


def test_get_top_committers_valid() -> None:
    raw_commits: list[dict[str, object]] = [
        {"commit": {"author": {"name": "Alice", "date": "2023-10-27T10:00:00Z"}}},
        {"commit": {"author": {"name": "Bob", "date": "2023-10-27T11:00:00Z"}}},
        {"commit": {"author": {"name": "Alice", "date": "2023-10-28T10:00:00Z"}}},
        {"commit": {"author": {"name": "Charlie", "date": "2023-10-28T11:00:00Z"}}},
    ]
    df = get_top_committers(raw_commits, top_n=2)
    assert df.shape == (2, 2)
    assert df.columns == ["name", "commit_count"]
    assert df.dtypes == [pl.String, pl.UInt32]

    results = df.to_dicts()
    assert results[0] == {"name": "Alice", "commit_count": 2}
    assert results[1] == {"name": "Bob", "commit_count": 1}


def test_get_top_committers_empty() -> None:
    raw_commits: list[dict[str, object]] = []
    df = get_top_committers(raw_commits)
    assert df.shape == (0, 2)
    assert df.columns == ["name", "commit_count"]
    assert df.dtypes == [pl.String, pl.UInt32]


def test_get_top_committers_deterministic_sorting() -> None:
    # 3 authors all have exactly 2 commits.
    # We want top 2. It should tie-break by name alphabetically ascending.
    raw_commits: list[dict[str, object]] = [
        {"commit": {"author": {"name": "Charlie", "date": "2023-10-27T10:00:00Z"}}},
        {"commit": {"author": {"name": "Charlie", "date": "2023-10-27T11:00:00Z"}}},
        {"commit": {"author": {"name": "Alice", "date": "2023-10-28T10:00:00Z"}}},
        {"commit": {"author": {"name": "Alice", "date": "2023-10-28T11:00:00Z"}}},
        {"commit": {"author": {"name": "Bob", "date": "2023-10-29T10:00:00Z"}}},
        {"commit": {"author": {"name": "Bob", "date": "2023-10-29T11:00:00Z"}}},
    ]
    df = get_top_committers(raw_commits, top_n=2)
    results = df.to_dicts()
    assert results[0] == {"name": "Alice", "commit_count": 2}
    assert results[1] == {"name": "Bob", "commit_count": 2}


def test_processing_validation_error() -> None:
    raw_commits: list[dict[str, object]] = [
        {"commit": {"author": {"name": "Alice"}}}  # Missing date
    ]
    with pytest.raises(ValidationError):
        aggregate_commits_by_date(raw_commits)

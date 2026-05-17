from datetime import date

import polars as pl
import pytest
from pydantic import ValidationError

from src.processing.transformations import aggregate_commits_by_date, get_top_committers


@pytest.fixture
def valid_mock_commits() -> list[dict[str, object]]:
    return [
        {"name": "Alice", "date": "2024-05-15T10:00:00Z"},
        {"name": "Alice", "date": "2024-05-15T11:00:00Z"},
        {"name": "Alice", "date": "2024-05-16T10:00:00Z"},
        {"name": "Bob", "date": "2024-05-15T10:00:00Z"},
        {"name": "Bob", "date": "2024-05-16T11:00:00Z"},
        {"name": "Charlie", "date": "2024-05-17T10:00:00Z"},
        {"name": "Charlie", "date": "2024-05-17T11:00:00Z"},
        {"name": "Charlie", "date": "2024-05-17T12:00:00Z"},
        {"name": "Dave", "date": "2024-05-16T10:00:00Z"},
        {"name": "Dave", "date": "2024-05-17T10:00:00Z"},
    ]


@pytest.fixture
def tie_mock_commits() -> list[dict[str, object]]:
    return [
        {"name": "Charlie", "date": "2024-05-15T10:00:00Z"},
        {"name": "Charlie", "date": "2024-05-15T11:00:00Z"},
        {"name": "Bob", "date": "2024-05-15T10:00:00Z"},
        {"name": "Bob", "date": "2024-05-15T11:00:00Z"},
        {"name": "Alice", "date": "2024-05-15T10:00:00Z"},
        {"name": "Alice", "date": "2024-05-15T11:00:00Z"},
    ]


def test_aggregate_commits_by_date_valid(valid_mock_commits: list[dict[str, object]]) -> None:
    df = aggregate_commits_by_date(valid_mock_commits)
    assert isinstance(df, pl.DataFrame)
    assert df.columns == ["date", "commit_count"]
    assert df.schema["date"] == pl.Date
    assert (
        df.schema["commit_count"] == pl.UInt32
        or df.schema["commit_count"] == pl.Int64
        or df.schema["commit_count"] == pl.UInt64
    )

    # 2024-05-15: Alice(2), Bob(1) = 3
    # 2024-05-16: Alice(1), Bob(1), Dave(1) = 3
    # 2024-05-17: Charlie(3), Dave(1) = 4
    results = df.to_dicts()
    assert len(results) == 3
    assert results[0] == {"date": date(2024, 5, 15), "commit_count": 3}
    assert results[1] == {"date": date(2024, 5, 16), "commit_count": 3}
    assert results[2] == {"date": date(2024, 5, 17), "commit_count": 4}


def test_aggregate_commits_by_date_empty() -> None:
    df = aggregate_commits_by_date([])
    assert isinstance(df, pl.DataFrame)
    assert df.columns == ["date", "commit_count"]
    assert len(df) == 0


def test_aggregate_commits_by_date_invalid() -> None:
    invalid_data: list[dict[str, object]] = [{"name": "Alice"}]
    with pytest.raises(ValidationError):
        aggregate_commits_by_date(invalid_data)


def test_get_top_committers_valid(valid_mock_commits: list[dict[str, object]]) -> None:
    df = get_top_committers(valid_mock_commits, top_n=2)
    assert isinstance(df, pl.DataFrame)
    assert df.columns == ["name", "commit_count"]
    results = df.to_dicts()
    assert len(results) == 2
    # Alphabetical sorting tie-breaker between Alice and Charlie
    assert results[0] == {"name": "Alice", "commit_count": 3}
    assert results[1] == {"name": "Charlie", "commit_count": 3}


def test_get_top_committers_tie_breaking(tie_mock_commits: list[dict[str, object]]) -> None:
    df = get_top_committers(tie_mock_commits, top_n=2)
    results = df.to_dicts()
    assert len(results) == 2
    assert results[0] == {"name": "Alice", "commit_count": 2}
    assert results[1] == {"name": "Bob", "commit_count": 2}


def test_get_top_committers_empty() -> None:
    df = get_top_committers([])
    assert isinstance(df, pl.DataFrame)
    assert df.columns == ["name", "commit_count"]
    assert len(df) == 0


def test_get_top_committers_invalid() -> None:
    invalid_data: list[dict[str, object]] = [{"name": "Alice"}]
    with pytest.raises(ValidationError):
        get_top_committers(invalid_data)

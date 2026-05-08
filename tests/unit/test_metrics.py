"""Unit tests for Polars metrics transformation."""

import polars as pl

from src.transformation.metrics import aggregate_daily_commits, get_top_committers


def test_aggregate_daily_commits() -> None:
    """Test aggregation of daily commits."""
    data = [
        {"date": "2023-01-01T12:00:00Z", "committer": "Alice"},
        {"date": "2023-01-01T15:00:00Z", "committer": "Bob"},
        {"date": "2023-01-02T10:00:00Z", "committer": "Alice"},
    ]
    df = aggregate_daily_commits(data)
    assert len(df) == 2
    # Convert 'date' column string values to actual python dates for assertion
    from datetime import date

    assert df.filter(pl.col("date") == date(2023, 1, 1))["commits"][0] == 2
    assert df.filter(pl.col("date") == date(2023, 1, 2))["commits"][0] == 1


def test_aggregate_daily_commits_empty() -> None:
    """Test aggregation with empty data."""
    df = aggregate_daily_commits([])
    assert len(df) == 0


def test_get_top_committers() -> None:
    """Test extraction of top committers."""
    data = [
        {"date": "2023-01-01", "committer": "Alice"},
        {"date": "2023-01-02", "committer": "Alice"},
        {"date": "2023-01-03", "committer": "Bob"},
        {"date": "2023-01-04", "committer": "Charlie"},
        {"date": "2023-01-05", "committer": "Dave"},
        {"date": "2023-01-06", "committer": "Eve"},
        {"date": "2023-01-07", "committer": "Frank"},
        {"date": "2023-01-08", "committer": "Frank"},
    ]
    df = get_top_committers(data, top_n=5)
    assert len(df) == 5
    # Frank and Alice have 2 commits, rest have 1.
    # Order should be Frank, Alice, Bob, Charlie, Dave (Eve gets dropped)
    # due to secondary sort by committer alphabetically
    assert df["committer"].to_list() == ["Alice", "Frank", "Bob", "Charlie", "Dave"]
    assert df["commits"].to_list() == [2, 2, 1, 1, 1]


def test_get_top_committers_empty() -> None:
    """Test top committers with empty data."""
    df = get_top_committers([])
    assert len(df) == 0

import datetime

import polars as pl

from src.domain_models.github import CommitInfo
from src.transformation.polars_engine import PolarsEngine


def create_mock_commit(sha: str, name: str, date_str: str) -> CommitInfo:
    return CommitInfo(
        sha=sha,
        commit={"message": "test", "committer": {"name": name, "date": date_str}},  # type: ignore[arg-type]
    )


def test_aggregate_commits_by_date() -> None:
    commits = [
        create_mock_commit("1", "Alice", "2023-01-01T10:00:00Z"),
        create_mock_commit("2", "Bob", "2023-01-01T12:00:00Z"),
        create_mock_commit("3", "Alice", "2023-01-02T10:00:00Z"),
    ]

    df = PolarsEngine.aggregate_commits_by_date(commits)

    expected_data = {
        "date": [datetime.date(2023, 1, 1), datetime.date(2023, 1, 2)],
        "commit_count": [2, 1],
    }
    expected_df = pl.DataFrame(expected_data, schema={"date": pl.Date, "commit_count": pl.UInt32})

    assert df.equals(expected_df)


def test_get_top_committers() -> None:
    commits = [
        create_mock_commit("1", "Alice", "2023-01-01T10:00:00Z"),
        create_mock_commit("2", "Bob", "2023-01-01T12:00:00Z"),
        create_mock_commit("3", "Alice", "2023-01-02T10:00:00Z"),
        create_mock_commit("4", "Charlie", "2023-01-02T10:00:00Z"),
        create_mock_commit("5", "Bob", "2023-01-02T10:00:00Z"),
        create_mock_commit("6", "Bob", "2023-01-02T10:00:00Z"),
        create_mock_commit("7", "Dave", "2023-01-02T10:00:00Z"),
        create_mock_commit("8", "Eve", "2023-01-02T10:00:00Z"),
        create_mock_commit("9", "Frank", "2023-01-02T10:00:00Z"),
    ]

    df = PolarsEngine.get_top_committers(commits, limit=5)

    expected_data = {
        "name": ["Bob", "Alice", "Charlie", "Dave", "Eve"],
        "commit_count": [3, 2, 1, 1, 1],
    }
    expected_df = pl.DataFrame(expected_data, schema={"name": pl.String, "commit_count": pl.UInt32})

    assert df.equals(expected_df)


def test_aggregate_empty() -> None:
    df = PolarsEngine.aggregate_commits_by_date([])
    assert df.is_empty()
    assert df.schema == {"date": pl.Date, "commit_count": pl.UInt32}


def test_top_committers_empty() -> None:
    df = PolarsEngine.get_top_committers([])
    assert df.is_empty()
    assert df.schema == {"name": pl.String, "commit_count": pl.UInt32}

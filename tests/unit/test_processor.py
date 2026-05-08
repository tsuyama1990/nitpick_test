from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

import polars as pl
import pytest

from src.domain_models import CommitInfo
from src.transformation.processor import DataProcessor


@pytest.fixture(autouse=True)
def mock_settings(tmp_path: Path) -> Iterator[None]:
    with patch("src.transformation.processor.get_settings") as mock_get_settings:
        mock_settings_obj = mock_get_settings.return_value
        mock_settings_obj.GITHUB_TOKEN = "dummy_token"  # noqa: S105
        mock_settings_obj.CACHE_DIR = str(tmp_path)
        yield


@pytest.fixture
def sample_commits() -> list[CommitInfo]:
    return [
        CommitInfo(
            sha="1", committer_name="User A", committer_date=datetime(2023, 1, 1, 12, 0, tzinfo=UTC)
        ),
        CommitInfo(
            sha="2", committer_name="User A", committer_date=datetime(2023, 1, 1, 15, 0, tzinfo=UTC)
        ),
        CommitInfo(
            sha="3", committer_name="User B", committer_date=datetime(2023, 1, 2, 10, 0, tzinfo=UTC)
        ),
        CommitInfo(
            sha="4", committer_name="User C", committer_date=datetime(2023, 1, 2, 11, 0, tzinfo=UTC)
        ),
        CommitInfo(
            sha="5", committer_name="User C", committer_date=datetime(2023, 1, 2, 12, 0, tzinfo=UTC)
        ),
        CommitInfo(
            sha="6", committer_name="User D", committer_date=datetime(2023, 1, 3, 10, 0, tzinfo=UTC)
        ),
        CommitInfo(
            sha="7", committer_name="User E", committer_date=datetime(2023, 1, 3, 11, 0, tzinfo=UTC)
        ),
        CommitInfo(
            sha="8", committer_name="User F", committer_date=datetime(2023, 1, 3, 12, 0, tzinfo=UTC)
        ),
    ]


def test_process_daily_commits(sample_commits: list[CommitInfo]) -> None:
    processor = DataProcessor()
    df = processor.process_daily_commits("test_owner", "test_repo", sample_commits)

    assert isinstance(df, pl.DataFrame)
    assert len(df) == 3
    # Check that sorting by date works
    dates = df["date"].to_list()
    assert str(dates[0]) == "2023-01-01"
    assert str(dates[1]) == "2023-01-02"
    assert str(dates[2]) == "2023-01-03"

    counts = df["commit_count"].to_list()
    assert counts[0] == 2
    assert counts[1] == 3
    assert counts[2] == 3


def test_process_top_committers(sample_commits: list[CommitInfo]) -> None:
    processor = DataProcessor()
    df = processor.process_top_committers("test_owner", "test_repo", sample_commits)

    assert isinstance(df, pl.DataFrame)
    # Should only return top 5
    assert len(df) <= 5

    names = df["committer_name"].to_list()
    counts = df["commit_count"].to_list()

    # User A and User C have 2 commits each
    assert "User A" in names[:2]
    assert "User C" in names[:2]
    assert counts[0] == 2
    assert counts[1] == 2


def test_caching_mechanism(sample_commits: list[CommitInfo]) -> None:
    processor = DataProcessor()

    # First call to generate and cache
    df1 = processor.process_daily_commits("cache_owner", "cache_repo", sample_commits)

    # Second call without commits should read from cache
    df2 = processor.process_daily_commits("cache_owner", "cache_repo")

    assert df1.equals(df2)


def test_caching_mechanism_top_committers(sample_commits: list[CommitInfo]) -> None:
    processor = DataProcessor()

    # First call to generate and cache
    df1 = processor.process_top_committers("cache_owner", "cache_repo", sample_commits)

    # Second call without commits should read from cache
    df2 = processor.process_top_committers("cache_owner", "cache_repo")

    assert df1.equals(df2)


def test_cache_miss_raises_error() -> None:
    processor = DataProcessor()
    with pytest.raises(ValueError, match="No valid cache found"):
        processor.process_daily_commits("miss_owner", "miss_repo")

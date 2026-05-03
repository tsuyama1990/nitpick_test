from datetime import UTC, datetime
from pathlib import Path

from src.domain_models import (
    AuthenticationError,
    CommitRecord,
    DashboardData,
    RepositoryMetadata,
)
from src.presentation.controller import get_dashboard_data
from src.processing.cache_manager import save_to_cache


def mock_fetch_metadata(repo: str) -> RepositoryMetadata:
    return RepositoryMetadata(
        owner=repo.split("/", maxsplit=1)[0],
        name=repo.split("/")[1] if "/" in repo else repo,
        star_count=100,
        fork_count=50,
        open_issue_count=10,
    )


def test_get_dashboard_data_happy_path(tmp_path: Path) -> None:
    repo_name = "test/repo_happy"

    called_commits = False

    def mock_fetch_commits(repo: str) -> list[CommitRecord]:
        nonlocal called_commits
        called_commits = True
        return [
            CommitRecord(commit_hash="123", author="alice", date=datetime(2023, 1, 1, tzinfo=UTC))
        ]

    from src.config import settings

    settings.cache_dir = tmp_path

    result = get_dashboard_data(repo_name, mock_fetch_metadata, mock_fetch_commits)

    assert called_commits is True
    assert isinstance(result, DashboardData)
    assert len(result.daily_commits_df) == 1
    assert len(result.top_committers_df) == 1


def test_get_dashboard_data_auth_error(tmp_path: Path) -> None:
    repo_name = "test/repo_error"

    def mock_fetch_metadata_error(repo: str) -> RepositoryMetadata:
        msg = "Authentication failed. Invalid or expired token."
        raise AuthenticationError(msg)

    def mock_fetch_commits(repo: str) -> list[CommitRecord]:
        return []

    from src.config import settings

    settings.cache_dir = tmp_path

    result = get_dashboard_data(repo_name, mock_fetch_metadata_error, mock_fetch_commits)

    assert isinstance(result, str)
    assert "Authentication failed" in result


def test_get_dashboard_data_cache_hit(tmp_path: Path) -> None:
    import polars as pl

    repo_name = "test/repo_hit"

    # Pre-populate cache
    daily_cache = pl.DataFrame({"date": ["2023-01-01"], "commit_count": [1]})
    top_cache = pl.DataFrame({"author": ["alice"], "commit_count": [1]})

    from src.config import settings

    settings.cache_dir = tmp_path
    save_to_cache(f"{repo_name}_daily", daily_cache)
    save_to_cache(f"{repo_name}_top", top_cache)

    called_commits = False

    def mock_fetch_commits(repo: str) -> list[CommitRecord]:
        nonlocal called_commits
        called_commits = True
        return []

    result = get_dashboard_data(repo_name, mock_fetch_metadata, mock_fetch_commits)

    assert called_commits is False
    assert isinstance(result, DashboardData)
    assert len(result.daily_commits_df) == 1
    assert len(result.top_committers_df) == 1

def test_get_dashboard_data_unexpected_error(tmp_path: Path) -> None:
    repo_name = "test/repo_unexpected"

    def mock_fetch_metadata_error(repo: str) -> RepositoryMetadata:
        raise ValueError("Something unexpected")

    def mock_fetch_commits(repo: str) -> list[CommitRecord]:
        return []

    from src.config import settings
    settings.cache_dir = tmp_path

    result = get_dashboard_data(repo_name, mock_fetch_metadata_error, mock_fetch_commits)
    assert isinstance(result, str)
    assert "unexpected error occurred" in result

from unittest.mock import MagicMock, patch

import polars as pl

from src.domain_models.dashboard import DashboardData
from src.domain_models.exceptions import GitHubAPIError
from src.domain_models.github import RepoMetadata
from src.presentation.controller import get_dashboard_data


@patch("src.presentation.controller.load_from_cache")
@patch("src.presentation.controller.load_metadata_cache")
@patch("src.presentation.controller.save_to_cache")
@patch("src.presentation.controller.save_metadata_cache")
@patch("src.presentation.controller.fetch_repo_metadata")
@patch("src.presentation.controller.fetch_commits")
def test_controller_cache_hit(
    mock_commits: MagicMock,
    mock_meta: MagicMock,
    mock_save_meta: MagicMock,
    mock_save: MagicMock,
    mock_load_meta: MagicMock,
    mock_load: MagicMock,
) -> None:
    # Mock cache hit
    mock_load.side_effect = [
        pl.DataFrame({"date": [], "commit_count": []}),  # daily
        pl.DataFrame({"author_name": [], "commit_count": []}),  # top
    ]
    mock_load_meta.return_value = {"stargazers_count": 1, "forks_count": 2, "open_issues_count": 3}

    result = get_dashboard_data("test/repo")

    # Verify
    assert isinstance(result, DashboardData)
    assert result.repo_metadata.stargazers_count == 1
    mock_commits.assert_not_called()
    mock_meta.assert_not_called()
    mock_save.assert_not_called()


@patch("src.presentation.controller.load_from_cache")
@patch("src.presentation.controller.load_metadata_cache")
@patch("src.presentation.controller.save_to_cache")
@patch("src.presentation.controller.save_metadata_cache")
@patch("src.presentation.controller.fetch_repo_metadata")
@patch("src.presentation.controller.fetch_commits")
def test_controller_cache_miss(
    mock_commits: MagicMock,
    mock_meta: MagicMock,
    mock_save_meta: MagicMock,
    mock_save: MagicMock,
    mock_load_meta: MagicMock,
    mock_load: MagicMock,
) -> None:
    # Mock cache miss
    mock_load.side_effect = [None, None]
    mock_load_meta.return_value = None

    # Mock API returns
    mock_meta.return_value = RepoMetadata(stargazers_count=10, forks_count=5, open_issues_count=2)
    mock_commits.return_value = []

    result = get_dashboard_data("test/repo")

    assert isinstance(result, DashboardData)
    assert result.repo_metadata.stargazers_count == 10
    mock_meta.assert_called_once()
    mock_commits.assert_called_once()
    assert mock_save.call_count == 2
    mock_save_meta.assert_called_once()


@patch("src.presentation.controller.load_from_cache")
@patch("src.presentation.controller.load_metadata_cache")
@patch("src.presentation.controller.fetch_repo_metadata")
def test_controller_api_error(
    mock_meta: MagicMock, mock_load_meta: MagicMock, mock_load: MagicMock
) -> None:
    mock_load.side_effect = [None, None]
    mock_load_meta.return_value = None
    mock_meta.side_effect = GitHubAPIError("API broken")

    result = get_dashboard_data("test/repo")

    assert isinstance(result, str)
    assert "unexpected error" in result


@patch("src.presentation.controller.load_from_cache")
@patch("src.presentation.controller.load_metadata_cache")
@patch("src.presentation.controller.fetch_repo_metadata")
def test_controller_repository_not_found(
    mock_meta: MagicMock, mock_load_meta: MagicMock, mock_load: MagicMock
) -> None:
    from src.domain_models.exceptions import RepositoryNotFoundError

    mock_load.side_effect = [None, None]
    mock_load_meta.return_value = None
    mock_meta.side_effect = RepositoryNotFoundError("Repo not found")

    result = get_dashboard_data("nonexistent/repo")

    assert isinstance(result, str)
    assert "Repository not found" in result


@patch("src.presentation.controller.load_from_cache")
@patch("src.presentation.controller.load_metadata_cache")
@patch("src.presentation.controller.fetch_repo_metadata")
def test_controller_rate_limit_error(
    mock_meta: MagicMock, mock_load_meta: MagicMock, mock_load: MagicMock
) -> None:
    from src.domain_models.exceptions import RateLimitError

    mock_load.side_effect = [None, None]
    mock_load_meta.return_value = None
    mock_meta.side_effect = RateLimitError("Rate limit exceeded")

    result = get_dashboard_data("test/repo")

    assert isinstance(result, str)
    assert "rate limit exceeded" in result.lower()


@patch("src.presentation.controller.load_from_cache")
@patch("src.presentation.controller.load_metadata_cache")
@patch("src.presentation.controller.fetch_repo_metadata")
def test_controller_unexpected_error(
    mock_meta: MagicMock, mock_load_meta: MagicMock, mock_load: MagicMock
) -> None:
    mock_load.side_effect = [None, None]
    mock_load_meta.return_value = None
    mock_meta.side_effect = Exception("Unexpected")

    result = get_dashboard_data("test/repo")

    assert isinstance(result, str)
    assert "unexpected system error" in result.lower()

from unittest.mock import MagicMock, patch

import polars as pl
import pytest

from src.domain_models.github import CommitInfo, RepoInfo
from src.ingestion.client import GitHubAPIError
from src.services.dashboard_controller import DashboardController
from src.services.exceptions import DashboardError
from src.storage.cache import CacheManager


@pytest.fixture
def mock_controller() -> DashboardController:
    with patch("src.ingestion.client.get_settings"):
        return DashboardController()


def test_validate_input_valid(mock_controller: DashboardController) -> None:
    owner, repo = mock_controller._validate_input("owner/repo")
    assert owner == "owner"
    assert repo == "repo"


def test_validate_input_invalid(mock_controller: DashboardController) -> None:
    with pytest.raises(DashboardError, match="Invalid format"):
        mock_controller._validate_input("invalid_repo")


@patch.object(CacheManager, "load")
@patch.object(CacheManager, "save")
@patch("src.services.dashboard_controller.GitHubClient")
def test_get_dashboard_data_cache_miss(
    mock_client_cls: MagicMock,
    mock_save: MagicMock,
    mock_load: MagicMock,
    mock_controller: DashboardController,
) -> None:
    # Setup mocks
    mock_client_instance = mock_client_cls.return_value
    mock_controller.client = mock_client_instance
    mock_load.return_value = None  # Cache miss

    mock_repo_info = RepoInfo(stargazers_count=10, forks_count=5, open_issues_count=1)
    mock_client_instance.get_repo_info.return_value = mock_repo_info

    # Needs valid CommitInfo to avoid empty dataframe structure mismatch errors in Polars transformation if not careful
    mock_commits: list[CommitInfo] = []
    mock_client_instance.get_recent_commits.return_value = mock_commits

    # Execute
    result = mock_controller.get_dashboard_data("owner/repo")

    # Assert
    assert result.cached is False
    assert result.repo_info == mock_repo_info
    mock_client_instance.get_recent_commits.assert_called_once_with("owner", "repo")
    assert mock_save.call_count == 2


@patch.object(CacheManager, "load")
@patch.object(CacheManager, "save")
@patch("src.services.dashboard_controller.GitHubClient")
def test_get_dashboard_data_cache_hit(
    mock_client_cls: MagicMock,
    mock_save: MagicMock,
    mock_load: MagicMock,
    mock_controller: DashboardController,
) -> None:
    # Setup mocks
    mock_client_instance = mock_client_cls.return_value
    mock_controller.client = mock_client_instance

    mock_repo_info = RepoInfo(stargazers_count=10, forks_count=5, open_issues_count=1)
    mock_client_instance.get_repo_info.return_value = mock_repo_info

    mock_df = pl.DataFrame()
    mock_load.return_value = mock_df  # Cache hit

    # Execute
    result = mock_controller.get_dashboard_data("owner/repo")

    # Assert
    assert result.cached is True
    assert result.commits_by_date.equals(mock_df)
    mock_client_instance.get_recent_commits.assert_not_called()
    mock_save.assert_not_called()


@patch("src.services.dashboard_controller.GitHubClient")
def test_get_dashboard_data_api_error(
    mock_client_cls: MagicMock, mock_controller: DashboardController
) -> None:
    mock_client_instance = mock_client_cls.return_value
    mock_controller.client = mock_client_instance
    mock_client_instance.get_repo_info.side_effect = GitHubAPIError("Not Found")

    with pytest.raises(DashboardError, match="Not Found"):
        mock_controller.get_dashboard_data("owner/repo")

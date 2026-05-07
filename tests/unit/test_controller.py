from collections.abc import Generator
from unittest.mock import MagicMock, patch

import polars as pl
import pytest

from src.domain_models import Repository
from src.ingestion.client import GitHubClientError
from src.presentation.controller import DashboardController


@pytest.fixture
def mock_dependencies() -> Generator[tuple[MagicMock, MagicMock, MagicMock], None, None]:
    with (
        patch("src.presentation.controller.GitHubClient") as MockClient,
        patch("src.presentation.controller.DataTransformer") as MockTransformer,
        patch("src.presentation.controller.CacheStorage") as MockCache,
    ):
        yield MockClient, MockTransformer, MockCache


def test_controller_cache_hit(mock_dependencies: tuple[MagicMock, MagicMock, MagicMock]) -> None:
    MockClient, MockTransformer, MockCache = mock_dependencies

    mock_repo = Repository(stargazers_count=1, forks_count=1, open_issues_count=1)
    mock_client_instance = MockClient.return_value
    mock_client_instance.get_repository_info.return_value = mock_repo

    mock_cache_instance = MockCache.return_value
    mock_cache_instance.get.side_effect = [pl.DataFrame({"date": []}), pl.DataFrame({"name": []})]

    controller = DashboardController()
    repo, by_date, top_users, err = controller.get_dashboard_data("owner", "repo")

    assert err is None
    assert repo == mock_repo
    assert by_date is not None
    assert top_users is not None
    mock_client_instance.get_recent_commits.assert_not_called()


def test_controller_cache_miss(mock_dependencies: tuple[MagicMock, MagicMock, MagicMock]) -> None:
    MockClient, MockTransformer, MockCache = mock_dependencies

    mock_repo = Repository(stargazers_count=1, forks_count=1, open_issues_count=1)
    mock_client_instance = MockClient.return_value
    mock_client_instance.get_repository_info.return_value = mock_repo
    mock_client_instance.get_recent_commits.return_value = []

    mock_cache_instance = MockCache.return_value
    mock_cache_instance.get.return_value = None

    mock_transformer_instance = MockTransformer.return_value
    mock_transformer_instance.process_commits.return_value = (
        pl.DataFrame({"date": []}),
        pl.DataFrame({"name": []}),
    )

    controller = DashboardController()
    repo, by_date, top_users, err = controller.get_dashboard_data("owner", "repo")

    assert err is None
    mock_client_instance.get_recent_commits.assert_called_once()
    mock_transformer_instance.process_commits.assert_called_once()
    assert mock_cache_instance.set.call_count == 2


def test_controller_repo_error(mock_dependencies: tuple[MagicMock, MagicMock, MagicMock]) -> None:
    MockClient, MockTransformer, MockCache = mock_dependencies
    mock_client_instance = MockClient.return_value
    mock_client_instance.get_repository_info.side_effect = GitHubClientError("Mock Error")

    controller = DashboardController()
    repo, by_date, top_users, err = controller.get_dashboard_data("owner", "repo")

    assert err == "Mock Error"
    assert repo is None


def test_controller_commits_error(
    mock_dependencies: tuple[MagicMock, MagicMock, MagicMock],
) -> None:
    MockClient, MockTransformer, MockCache = mock_dependencies
    mock_client_instance = MockClient.return_value
    mock_client_instance.get_repository_info.return_value = Repository(
        stargazers_count=1, forks_count=1, open_issues_count=1
    )
    mock_client_instance.get_recent_commits.side_effect = GitHubClientError("Mock Commits Error")

    mock_cache_instance = MockCache.return_value
    mock_cache_instance.get.return_value = None

    controller = DashboardController()
    repo, by_date, top_users, err = controller.get_dashboard_data("owner", "repo")

    assert err == "Mock Commits Error"
    assert repo is not None

import pytest
from pytest_mock import MockerFixture

from src.domain_models import Commit, InvalidPayloadError, RepositoryMetrics
from src.ingestion.github_client import GitHubClient
from src.processing.service import GitHubAnalyticsService


def test_github_analytics_service_metrics(mocker: MockerFixture) -> None:
    mock_client = mocker.Mock(spec=GitHubClient)
    # Include an extra field to test filtering
    mock_client.get_repository_metrics.return_value = {
        "stargazers_count": 100,
        "forks_count": 50,
        "open_issues_count": 10,
        "unexpected_field": "ignore_me",
    }

    service = GitHubAnalyticsService(client=mock_client)
    metrics = service.get_metrics("owner", "repo")

    assert isinstance(metrics, RepositoryMetrics)
    assert metrics.stargazers_count == 100
    assert metrics.forks_count == 50
    assert metrics.open_issues_count == 10
    assert not hasattr(metrics, "unexpected_field")
    mock_client.get_repository_metrics.assert_called_once_with("owner", "repo")


def test_github_analytics_service_commits(mocker: MockerFixture) -> None:
    mock_client = mocker.Mock(spec=GitHubClient)
    mock_client.get_recent_commits.return_value = [
        {"sha": "abc", "extra": "data"},
        {"sha": "def", "extra": "data2"},
    ]

    service = GitHubAnalyticsService(client=mock_client)
    commits = service.get_commits("owner", "repo", limit=5)

    assert isinstance(commits, list)
    assert len(commits) == 2
    assert isinstance(commits[0], Commit)
    assert commits[0].sha == "abc"
    assert not hasattr(commits[0], "extra")
    mock_client.get_recent_commits.assert_called_once_with("owner", "repo", 5)


def test_github_analytics_service_invalid_payload(mocker: MockerFixture) -> None:
    mock_client = mocker.Mock(spec=GitHubClient)
    # Missing stargazers_count should trigger ValidationError
    mock_client.get_repository_metrics.return_value = {
        "forks_count": 50,
        "open_issues_count": 10,
    }

    service = GitHubAnalyticsService(client=mock_client)
    with pytest.raises(InvalidPayloadError, match="Failed to validate repository metrics:"):
        service.get_metrics("owner", "repo")


def test_github_analytics_service_invalid_commit_payload(mocker: MockerFixture) -> None:
    mock_client = mocker.Mock(spec=GitHubClient)
    # Missing sha should trigger ValidationError
    mock_client.get_recent_commits.return_value = [
        {"not_sha": "abc"},
    ]

    service = GitHubAnalyticsService(client=mock_client)
    with pytest.raises(InvalidPayloadError, match="Failed to validate commit payload:"):
        service.get_commits("owner", "repo")

from collections.abc import Generator

import pytest
from pytest_httpx import HTTPXMock

from src.domain_models import RateLimitExceededError, RepositoryNotFoundError
from src.ingestion.github_client import GitHubClient


@pytest.fixture
def github_client() -> Generator[GitHubClient, None, None]:
    """Provides a GitHubClient instance with a test token."""
    with GitHubClient(token="test_token") as client:  # noqa: S106
        yield client


def test_github_client_initialization(github_client: GitHubClient) -> None:
    """Test that the client initializes with correct headers and base URL."""
    assert github_client.client.base_url == "https://api.github.com"
    headers = github_client.client.headers
    assert headers["Accept"] == "application/vnd.github.v3+json"
    assert headers["Authorization"] == "Bearer test_token"


def test_get_repository_metrics_success(github_client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    """Test successful retrieval of repository metrics."""
    mock_response = {
        "stargazers_count": 100,
        "forks_count": 50,
        "open_issues_count": 10,
    }
    httpx_mock.add_response(
        url="https://api.github.com/repos/test_owner/test_repo",
        json=mock_response,
        status_code=200,
    )

    metrics = github_client.get_repository_metrics("test_owner", "test_repo")
    assert metrics == mock_response


def test_get_recent_commits_success(github_client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    """Test successful retrieval of recent commits."""
    mock_response = [{"sha": "abc1234"}, {"sha": "def5678"}]
    httpx_mock.add_response(
        url="https://api.github.com/repos/test_owner/test_repo/commits?per_page=100",
        json=mock_response,
        status_code=200,
    )

    commits = github_client.get_recent_commits("test_owner", "test_repo")
    assert commits == mock_response


def test_get_repository_metrics_not_found(
    github_client: GitHubClient, httpx_mock: HTTPXMock
) -> None:
    """Test handling of 404 Not Found error."""
    httpx_mock.add_response(
        url="https://api.github.com/repos/invalid/invalid",
        status_code=404,
    )

    with pytest.raises(RepositoryNotFoundError, match="Repository not found"):
        github_client.get_repository_metrics("invalid", "invalid")


def test_get_repository_metrics_rate_limit(
    github_client: GitHubClient, httpx_mock: HTTPXMock
) -> None:
    """Test handling of 403 Rate Limit error."""
    httpx_mock.add_response(
        url="https://api.github.com/repos/test_owner/test_repo",
        status_code=403,
        text="Rate limit exceeded",
    )

    with pytest.raises(RateLimitExceededError, match="Rate limit exceeded"):
        github_client.get_repository_metrics("test_owner", "test_repo")


def test_get_recent_commits_rate_limit(github_client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    """Test handling of 429 Rate Limit error on commits endpoint."""
    httpx_mock.add_response(
        url="https://api.github.com/repos/test_owner/test_repo/commits?per_page=100",
        status_code=429,
        text="Too many requests",
    )

    with pytest.raises(RateLimitExceededError, match="Rate limit exceeded"):
        github_client.get_recent_commits("test_owner", "test_repo")


def test_get_repository_metrics_invalid_json(
    github_client: GitHubClient, httpx_mock: HTTPXMock
) -> None:
    """Test handling of invalid JSON response (not a dict)."""
    httpx_mock.add_response(
        url="https://api.github.com/repos/test_owner/test_repo",
        json=[],  # Return a list instead of dict
        status_code=200,
    )

    with pytest.raises(TypeError, match="Expected a dictionary response"):
        github_client.get_repository_metrics("test_owner", "test_repo")


def test_get_recent_commits_invalid_json(
    github_client: GitHubClient, httpx_mock: HTTPXMock
) -> None:
    """Test handling of invalid JSON response (not a list)."""
    httpx_mock.add_response(
        url="https://api.github.com/repos/test_owner/test_repo/commits?per_page=100",
        json={},  # Return a dict instead of list
        status_code=200,
    )

    with pytest.raises(TypeError, match="Expected a list response"):
        github_client.get_recent_commits("test_owner", "test_repo")

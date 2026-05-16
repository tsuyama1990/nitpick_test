import os

import pytest
from pytest_httpx import HTTPXMock

from src.domain_models.config import Settings
from src.domain_models.exceptions import RateLimitExceededError, RepositoryNotFoundError
from src.domain_models.schemas import CommitHistory, RepositoryMetrics
from src.ingestion.github_client import GitHubClient


def test_github_client_initialization() -> None:
    """Verify that the GitHubClient constructs the httpx.Client with correct headers."""
    settings = Settings(GITHUB_TOKEN="test_token_123")  # noqa: S106

    with GitHubClient(settings=settings) as client:
        assert client.client.base_url == "https://api.github.com"
        assert client.client.headers["Accept"] == "application/vnd.github.v3+json"
        assert client.client.headers["Authorization"] == f"Bearer {settings.GITHUB_TOKEN}"
        assert client.client.timeout.read == 10.0


def test_github_client_initialization_no_token() -> None:
    """Verify that ValueError is raised if token is empty."""
    settings = Settings(GITHUB_TOKEN="")

    with pytest.raises(ValueError, match="GitHub token must be provided via Settings"):
        GitHubClient(settings=settings)


def test_get_repository_metrics_success(httpx_mock: HTTPXMock) -> None:
    """Verify successful retrieval of repository metrics."""
    mock_response = {
        "stargazers_count": 100,
        "forks_count": 50,
        "open_issues_count": 10,
    }
    httpx_mock.add_response(
        url="https://api.github.com/repos/test-owner/test-repo",
        json=mock_response,
        status_code=200,
    )

    settings = Settings(GITHUB_TOKEN="mock")  # noqa: S106
    with GitHubClient(settings=settings) as client:
        result = client.get_repository_metrics("test-owner", "test-repo")

    assert isinstance(result, RepositoryMetrics)
    assert result.stargazers_count == 100
    assert result.forks_count == 50
    assert result.open_issues_count == 10


def test_get_recent_commits_success(httpx_mock: HTTPXMock) -> None:
    """Verify successful retrieval of recent commits."""
    mock_response = [
        {"sha": "abc1234", "commit": {"author": {"name": "Test User", "date": "2024-01-01"}}}
    ]
    httpx_mock.add_response(
        url="https://api.github.com/repos/test-owner/test-repo/commits?per_page=100",
        json=mock_response,
        status_code=200,
    )

    settings = Settings(GITHUB_TOKEN="mock")  # noqa: S106
    with GitHubClient(settings=settings) as client:
        result = client.get_recent_commits("test-owner", "test-repo", limit=100)

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], CommitHistory)
    assert result[0].sha == "abc1234"
    assert result[0].author == "Test User"
    assert result[0].date == "2024-01-01"


def test_github_client_404_error(httpx_mock: HTTPXMock) -> None:
    """Verify that a 404 response raises a RepositoryNotFoundError."""
    httpx_mock.add_response(
        url="https://api.github.com/repos/invalid-owner/invalid-repo",
        status_code=404,
    )

    settings = Settings(GITHUB_TOKEN="mock")  # noqa: S106
    with (
        GitHubClient(settings=settings) as client,
        pytest.raises(
            RepositoryNotFoundError, match="Repository invalid-owner/invalid-repo not found"
        ),
    ):
        client.get_repository_metrics("invalid-owner", "invalid-repo")


def test_github_client_rate_limit_error(httpx_mock: HTTPXMock) -> None:
    """Verify that a 403 or 429 response raises a RateLimitExceededError."""
    httpx_mock.add_response(
        url="https://api.github.com/repos/test-owner/test-repo",
        status_code=403,
    )

    settings = Settings(GITHUB_TOKEN="mock")  # noqa: S106
    with GitHubClient(settings=settings) as client:
        with pytest.raises(RateLimitExceededError, match="GitHub API rate limit exceeded"):
            client.get_repository_metrics("test-owner", "test-repo")

        httpx_mock.add_response(
            url="https://api.github.com/repos/test-owner/test-repo/commits?per_page=10",
            status_code=429,
        )
        with pytest.raises(RateLimitExceededError, match="GitHub API rate limit exceeded"):
            client.get_recent_commits("test-owner", "test-repo", limit=10)


@pytest.mark.skip(reason="Live API test")
def test_live_api_get_metrics() -> None:
    """Live test verifying network path and JSON structure alignment against real API."""
    token = os.getenv("GITHUB_TOKEN", "").strip()
    if not token:
        pytest.skip("GITHUB_TOKEN not found in environment.")

    settings = Settings(GITHUB_TOKEN=token)
    with GitHubClient(settings=settings) as client:
        result = client.get_repository_metrics("streamlit", "streamlit")

    assert isinstance(result, RepositoryMetrics)
    assert result.stargazers_count > 0

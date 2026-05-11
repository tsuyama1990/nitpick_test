import os
from unittest.mock import patch

import pytest
from pytest_httpx import HTTPXMock

from src.domain_models.config import get_settings
from src.domain_models.exceptions import RateLimitExceededError, RepositoryNotFoundError
from src.ingestion.github_client import GitHubClient


@pytest.fixture(autouse=True)
def clear_settings_cache() -> None:
    get_settings.cache_clear()


@patch.dict(os.environ, {"GITHUB_TOKEN": "fake-token"}, clear=True)
def test_github_client_initialization() -> None:
    client = GitHubClient()
    assert client.client.headers.get("Accept") == "application/vnd.github.v3+json"
    assert client.client.headers.get("Authorization") == "Bearer fake-token"


@patch.dict(os.environ, {"GITHUB_TOKEN": "fake-token"}, clear=True)
def test_get_repository_metrics_success(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test-owner/test-repo",
        json={"stargazers_count": 100, "forks_count": 50, "open_issues_count": 10},
    )

    client = GitHubClient()
    result = client.get_repository_metrics("test-owner", "test-repo")

    assert result == {"stargazers_count": 100, "forks_count": 50, "open_issues_count": 10}


@patch.dict(os.environ, {"GITHUB_TOKEN": "fake-token"}, clear=True)
def test_get_repository_metrics_not_found(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test-owner/test-repo",
        status_code=404,
    )

    client = GitHubClient()
    with pytest.raises(RepositoryNotFoundError):
        client.get_repository_metrics("test-owner", "test-repo")


@patch.dict(os.environ, {"GITHUB_TOKEN": "fake-token"}, clear=True)
def test_get_repository_metrics_rate_limit(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test-owner/test-repo",
        status_code=403,
    )

    client = GitHubClient()
    with pytest.raises(RateLimitExceededError):
        client.get_repository_metrics("test-owner", "test-repo")


@patch.dict(os.environ, {"GITHUB_TOKEN": "fake-token"}, clear=True)
def test_get_recent_commits_success(httpx_mock: HTTPXMock) -> None:
    mock_commits = [{"sha": "123", "commit": {"message": "init"}}]
    httpx_mock.add_response(
        url="https://api.github.com/repos/test-owner/test-repo/commits?per_page=100",
        json=mock_commits,
    )

    client = GitHubClient()
    result = client.get_recent_commits("test-owner", "test-repo")

    assert result == mock_commits


@patch.dict(os.environ, {"GITHUB_TOKEN": "fake-token"}, clear=True)
def test_get_recent_commits_rate_limit(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test-owner/test-repo/commits?per_page=100",
        status_code=429,
    )

    client = GitHubClient()
    with pytest.raises(RateLimitExceededError):
        client.get_recent_commits("test-owner", "test-repo")


@pytest.mark.skip(reason="Live API test")
def test_live_get_repository_metrics() -> None:
    client = GitHubClient()
    result = client.get_repository_metrics("streamlit", "streamlit")
    assert "stargazers_count" in result

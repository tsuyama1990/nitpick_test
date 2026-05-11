import os
from collections.abc import Generator
from unittest.mock import patch

import pytest
from pytest_httpx import HTTPXMock

from src.domain_models.config import get_settings
from src.domain_models.exceptions import (
    GitHubAnalyticsError,
    RateLimitExceededError,
    RepositoryNotFoundError,
)
from src.ingestion.github_client import GitHubClient


@pytest.fixture(autouse=True)
def _setup_env() -> Generator[None, None, None]:
    with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}, clear=True):
        get_settings.cache_clear()
        yield


def test_get_repository_metrics_success(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/repo",
        json={"stargazers_count": 10, "forks_count": 5, "open_issues_count": 2},
    )
    client = GitHubClient()
    metrics = client.get_repository_metrics("owner", "repo")
    assert metrics["stargazers_count"] == 10
    assert metrics["forks_count"] == 5


def test_get_recent_commits_success(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/repo/commits?per_page=2",
        json=[{"sha": "1"}, {"sha": "2"}],
    )
    client = GitHubClient()
    commits = client.get_recent_commits("owner", "repo", limit=2)
    assert len(commits) == 2
    assert commits[0]["sha"] == "1"


def test_handle_response_404(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url="https://api.github.com/repos/owner/repo", status_code=404)
    client = GitHubClient()
    with pytest.raises(RepositoryNotFoundError, match="Repository not found"):
        client.get_repository_metrics("owner", "repo")


def test_handle_response_rate_limit(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url="https://api.github.com/repos/owner/repo", status_code=403)
    client = GitHubClient()
    with pytest.raises(RateLimitExceededError, match="rate limit exceeded"):
        client.get_repository_metrics("owner", "repo")


def test_handle_response_other_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/repo", status_code=500, text="Internal Error"
    )
    client = GitHubClient()
    with pytest.raises(GitHubAnalyticsError, match="GitHub API error: 500"):
        client.get_repository_metrics("owner", "repo")


def test_handle_response_unexpected_format_metrics(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/repo", json=["not", "a", "dict"]
    )
    client = GitHubClient()
    with pytest.raises(GitHubAnalyticsError, match="Expected dictionary response for metrics"):
        client.get_repository_metrics("owner", "repo")


def test_handle_response_unexpected_format_commits(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/repo/commits?per_page=100",
        json={"not": "a list"},
    )
    client = GitHubClient()
    with pytest.raises(GitHubAnalyticsError, match="Expected list response for commits"):
        client.get_recent_commits("owner", "repo")


def test_handle_response_completely_invalid_json(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/repo", json="a string, not dict or list"
    )
    client = GitHubClient()
    with pytest.raises(GitHubAnalyticsError, match="Unexpected JSON response format"):
        client.get_repository_metrics("owner", "repo")


def test_get_recent_commits_fallback_limit(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/repo/commits?per_page=100",
        json=[{"sha": "1"}],
    )
    client = GitHubClient()
    commits = client.get_recent_commits("owner", "repo")
    assert len(commits) == 1

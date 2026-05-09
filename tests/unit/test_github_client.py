from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from pytest_httpx import HTTPXMock

from src.domain_models import Commit, Repository
from src.github_client import GitHubAPIError, GitHubClient, RateLimitError


@pytest.fixture
def mock_settings() -> Generator[MagicMock, None, None]:
    with patch("src.github_client.get_settings") as mock:
        mock.return_value.GITHUB_TOKEN = "dummy_token"
        yield mock


def test_get_repository_info_success(httpx_mock: HTTPXMock, mock_settings: MagicMock) -> None:
    """Should fetch repository info and parse it into a Repository model."""
    client = GitHubClient()

    # Mock response
    mock_payload = {
        "id": 12345,
        "name": "test-repo",
        "full_name": "owner/test-repo",
        "stargazers_count": 100,
        "forks_count": 50,
        "open_issues_count": 5,
        "extra_field": "ignore me",
    }

    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/test-repo", json=mock_payload, status_code=200
    )

    repo = client.get_repository_info("owner", "test-repo")

    assert isinstance(repo, Repository)
    assert repo.id == 12345
    assert repo.stargazers_count == 100
    assert not hasattr(repo, "extra_field")

    # Verify token injection
    request = httpx_mock.get_request()
    assert request is not None
    assert request.headers.get("Authorization") == "token dummy_token"


def test_get_recent_commits_success(httpx_mock: HTTPXMock, mock_settings: MagicMock) -> None:
    """Should fetch recent commits and parse them into a list of Commit models."""
    client = GitHubClient()

    mock_payload = [
        {
            "sha": "abc1234",
            "commit": {
                "author": {
                    "name": "Author 1",
                    "email": "author1@test.com",
                    "date": "2024-01-01T12:00:00Z",
                },
                "message": "Commit message 1",
            },
            "url": "ignore",
        },
        {
            "sha": "def5678",
            "commit": {
                "author": {
                    "name": "Author 2",
                    "email": "author2@test.com",
                    "date": "2024-01-02T12:00:00Z",
                },
                "message": "Commit message 2",
            },
            "url": "ignore",
        },
    ]

    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/test-repo/commits?per_page=100",
        json=mock_payload,
        status_code=200,
    )

    commits = client.get_recent_commits("owner", "test-repo", limit=100)

    assert len(commits) == 2
    assert isinstance(commits[0], Commit)
    assert commits[0].sha == "abc1234"
    assert commits[0].commit.message == "Commit message 1"
    assert commits[1].sha == "def5678"


def test_github_client_rate_limit(httpx_mock: HTTPXMock, mock_settings: MagicMock) -> None:
    """Should raise RateLimitError on 403 or 429 status code."""
    client = GitHubClient()

    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/test-repo",
        status_code=403,
        json={"message": "API rate limit exceeded"},
    )

    with pytest.raises(RateLimitError, match="Rate limit exceeded"):
        client.get_repository_info("owner", "test-repo")


def test_github_client_api_error(httpx_mock: HTTPXMock, mock_settings: MagicMock) -> None:
    """Should raise GitHubAPIError on other non-2xx status codes."""
    client = GitHubClient()

    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/test-repo",
        status_code=404,
        json={"message": "Not Found"},
    )

    with pytest.raises(GitHubAPIError, match="API request failed with status 404"):
        client.get_repository_info("owner", "test-repo")

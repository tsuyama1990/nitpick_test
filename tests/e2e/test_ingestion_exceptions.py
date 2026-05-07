import pytest
from pytest_httpx import HTTPXMock

from src.ingestion import AuthError, GitHubClient, NotFoundError, RateLimitError


def test_auth_error_handling(monkeypatch: pytest.MonkeyPatch, httpx_mock: HTTPXMock) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "fake_test_token")
    client = GitHubClient()

    httpx_mock.add_response(
        url="https://api.github.com/repos/test-owner/test-repo",
        status_code=401,
        json={"message": "Bad credentials"},
    )

    with pytest.raises(AuthError, match="Authentication failed"):
        client.fetch_repository_info("test-owner", "test-repo")


def test_rate_limit_error_handling(monkeypatch: pytest.MonkeyPatch, httpx_mock: HTTPXMock) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "fake_test_token")
    client = GitHubClient()

    httpx_mock.add_response(
        url="https://api.github.com/repos/test-owner/test-repo",
        status_code=403,
        json={"message": "API rate limit exceeded"},
    )

    with pytest.raises(RateLimitError, match="Rate limit exceeded"):
        client.fetch_repository_info("test-owner", "test-repo")

    httpx_mock.add_response(
        url="https://api.github.com/repos/test-owner/test-repo/commits?per_page=100",
        status_code=429,
        json={"message": "Too Many Requests"},
    )

    with pytest.raises(RateLimitError, match="Rate limit exceeded"):
        client.fetch_recent_commits("test-owner", "test-repo")


def test_not_found_error_handling(monkeypatch: pytest.MonkeyPatch, httpx_mock: HTTPXMock) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "fake_test_token")
    client = GitHubClient()

    httpx_mock.add_response(
        url="https://api.github.com/repos/test-owner/not-a-real-repo",
        status_code=404,
        json={"message": "Not Found"},
    )

    with pytest.raises(NotFoundError, match="Repository not found"):
        client.fetch_repository_info("test-owner", "not-a-real-repo")

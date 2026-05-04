from datetime import UTC, datetime

import pytest
from pytest_httpx import HTTPXMock

from src.domain_models.exceptions import (
    AuthenticationError,
    GitHubAPIError,
    RateLimitError,
    RepositoryNotFoundError,
)
from src.ingestion.github_client import GitHubClient


def test_fetch_repository_metadata_success(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/streamlit/streamlit",
        json={
            "name": "streamlit",
            "owner": {"login": "streamlit"},
            "stargazers_count": 15000,
            "forks_count": 1500,
            "open_issues_count": 200,
            "extra_field": "ignore_me",
        },
    )

    client = GitHubClient(token="dummy_token")  # noqa: S106
    repo = client.fetch_repository_metadata("streamlit", "streamlit")

    assert repo.name == "streamlit"
    assert repo.owner == "streamlit"
    assert repo.stargazers_count == 15000
    assert repo.forks_count == 1500


def test_fetch_commit_history_success(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/streamlit/streamlit/commits?per_page=100",
        json=[
            {
                "sha": "123456",
                "commit": {"author": {"name": "John Doe", "date": "2023-10-01T12:00:00Z"}},
                "extra": "ignore_me",
            }
        ],
    )

    client = GitHubClient(token="dummy_token")  # noqa: S106
    commits = client.fetch_commit_history("streamlit", "streamlit")

    assert len(commits) == 1
    assert commits[0].sha == "123456"
    assert commits[0].author_name == "John Doe"
    assert commits[0].date == datetime(2023, 10, 1, 12, 0, tzinfo=UTC)


def test_fetch_repository_not_found(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url="https://api.github.com/repos/invalid/repo", status_code=404)

    client = GitHubClient(token="dummy_token")  # noqa: S106
    with pytest.raises(RepositoryNotFoundError):
        client.fetch_repository_metadata("invalid", "repo")


def test_authentication_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url="https://api.github.com/repos/streamlit/streamlit", status_code=401)

    client = GitHubClient(token="dummy_token")  # noqa: S106
    with pytest.raises(AuthenticationError):
        client.fetch_repository_metadata("streamlit", "streamlit")


def test_rate_limit_error_429(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url="https://api.github.com/repos/streamlit/streamlit", status_code=429)

    client = GitHubClient(token="dummy_token")  # noqa: S106
    with pytest.raises(RateLimitError):
        client.fetch_repository_metadata("streamlit", "streamlit")


def test_rate_limit_error_403(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/streamlit/streamlit",
        status_code=403,
        text="API rate limit exceeded",
    )

    client = GitHubClient(token="dummy_token")  # noqa: S106
    with pytest.raises(RateLimitError):
        client.fetch_repository_metadata("streamlit", "streamlit")


def test_generic_api_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url="https://api.github.com/repos/streamlit/streamlit", status_code=500)

    client = GitHubClient(token="dummy_token")  # noqa: S106
    with pytest.raises(GitHubAPIError):
        client.fetch_repository_metadata("streamlit", "streamlit")


def test_missing_token() -> None:
    from src.config import get_settings

    settings = get_settings()
    original_token = settings.GITHUB_TOKEN
    settings.GITHUB_TOKEN = None
    try:
        with pytest.raises(ValueError, match="GitHub Token is missing"):
            GitHubClient(token=None)
    finally:
        settings.GITHUB_TOKEN = original_token

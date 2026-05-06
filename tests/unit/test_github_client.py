from datetime import UTC, datetime

import pytest
from pytest_httpx import HTTPXMock

from src.domain_models.exceptions import (
    AuthenticationError,
    RateLimitError,
    RepositoryNotFoundError,
)
from src.domain_models.models import CommitRecord, RepositoryMetadata
from src.ingestion.github_client import GitHubClient


@pytest.fixture
def github_client() -> GitHubClient:
    return GitHubClient(token="mocked_token")  # noqa: S106


def test_get_repository_metadata_success(
    github_client: GitHubClient, httpx_mock: HTTPXMock
) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/streamlit/streamlit",
        json={
            "name": "streamlit",
            "owner": {"login": "streamlit"},
            "stargazers_count": 1000,
            "forks_count": 500,
            "open_issues_count": 100,
        },
    )

    metadata = github_client.get_repository_metadata("streamlit", "streamlit")

    assert isinstance(metadata, RepositoryMetadata)
    assert metadata.owner == "streamlit"
    assert metadata.repo == "streamlit"
    assert metadata.star_count == 1000
    assert metadata.fork_count == 500
    assert metadata.open_issue_count == 100


def test_get_commits_success(github_client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/streamlit/streamlit/commits?per_page=100",
        json=[
            {
                "sha": "1234567890abcdef",
                "commit": {
                    "author": {"name": "Test Author", "date": "2023-10-27T10:00:00Z"},
                },
            }
        ],
    )

    commits = github_client.get_commits("streamlit", "streamlit")

    assert len(commits) == 1
    commit = commits[0]
    assert isinstance(commit, CommitRecord)
    assert commit.commit_hash == "1234567890abcdef"
    assert commit.author_name == "Test Author"
    assert commit.date == datetime(2023, 10, 27, 10, 0, tzinfo=UTC)


@pytest.mark.parametrize("status_code", [401, 403])
def test_authentication_error(
    github_client: GitHubClient, httpx_mock: HTTPXMock, status_code: int
) -> None:
    # 403 is treated as RateLimitError if specific headers are present, else AuthError
    # We test AuthError here without rate limit headers
    httpx_mock.add_response(
        url="https://api.github.com/repos/streamlit/streamlit",
        status_code=status_code,
        json={"message": "Bad credentials"},
    )

    with pytest.raises(AuthenticationError):
        github_client.get_repository_metadata("streamlit", "streamlit")


def test_rate_limit_error_429(github_client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/streamlit/streamlit",
        status_code=429,
        json={"message": "Too Many Requests"},
    )

    with pytest.raises(RateLimitError):
        github_client.get_repository_metadata("streamlit", "streamlit")


def test_rate_limit_error_403_headers(github_client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/streamlit/streamlit",
        status_code=403,
        headers={"x-ratelimit-remaining": "0"},
        json={"message": "API rate limit exceeded"},
    )

    with pytest.raises(RateLimitError):
        github_client.get_repository_metadata("streamlit", "streamlit")


def test_repository_not_found(github_client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/nonexistent/repo",
        status_code=404,
        json={"message": "Not Found"},
    )

    with pytest.raises(RepositoryNotFoundError):
        github_client.get_repository_metadata("nonexistent", "repo")

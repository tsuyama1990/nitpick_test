import os

import pytest
from pytest_httpx import HTTPXMock

from src.domain_models.config import Settings, get_settings
from src.domain_models.exceptions import (
    AuthenticationError,
    RateLimitError,
    RepositoryNotFoundError,
)
from src.domain_models.github import CommitRecord, RepositoryMetadata
from src.ingestion.github_client import GitHubClient


def test_fetch_repository_metadata_success(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test-owner/test-repo",
        json={
            "name": "test-repo",
            "owner": {"login": "test-owner"},
            "stargazers_count": 100,
            "forks_count": 50,
            "open_issues_count": 10,
        },
    )

    client = GitHubClient(token=os.getenv("GITHUB_TOKEN"))
    metadata = client.fetch_repository_metadata("test-owner", "test-repo")

    assert isinstance(metadata, RepositoryMetadata)
    assert metadata.name == "test-repo"
    assert metadata.owner == "test-owner"
    assert metadata.star_count == 100
    assert metadata.fork_count == 50
    assert metadata.open_issue_count == 10


def test_fetch_commit_history_success(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test-owner/test-repo/commits?per_page=100",
        json=[
            {
                "sha": "abc123def456",
                "commit": {"author": {"name": "Test Author", "date": "2023-01-01T12:00:00Z"}},
            }
        ],
    )

    client = GitHubClient()
    commits = client.fetch_commit_history("test-owner", "test-repo")

    assert len(commits) == 1
    assert isinstance(commits[0], CommitRecord)
    assert commits[0].commit_hash == "abc123def456"
    assert commits[0].author_name == "Test Author"
    assert commits[0].date.year == 2023


def test_fetch_repository_metadata_not_found(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/invalid/invalid",
        status_code=404,
        json={"message": "Not Found"},
    )

    client = GitHubClient()
    with pytest.raises(RepositoryNotFoundError):
        client.fetch_repository_metadata("invalid", "invalid")


def test_fetch_repository_metadata_auth_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test-owner/test-repo",
        status_code=401,
        json={"message": "Bad credentials"},
    )

    client = GitHubClient()
    with pytest.raises(AuthenticationError):
        client.fetch_repository_metadata("test-owner", "test-repo")


def test_fetch_repository_metadata_rate_limit(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test-owner/test-repo",
        status_code=429,
        json={"message": "API rate limit exceeded"},
    )

    client = GitHubClient(token="explicit-token")  # noqa: S106
    with pytest.raises(RateLimitError):
        client.fetch_repository_metadata("test-owner", "test-repo")


def test_fetch_repository_metadata_rate_limit_403(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test-owner/test-repo",
        status_code=403,
        headers={"x-ratelimit-remaining": "0"},
        json={"message": "API rate limit exceeded"},
    )

    client = GitHubClient()
    with pytest.raises(RateLimitError):
        client.fetch_repository_metadata("test-owner", "test-repo")


def test_fetch_repository_metadata_forbidden_403(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test-owner/test-repo",
        status_code=403,
        headers={"x-ratelimit-remaining": "10"},
        json={"message": "Forbidden"},
    )

    client = GitHubClient()
    with pytest.raises(AuthenticationError):
        client.fetch_repository_metadata("test-owner", "test-repo")


def test_fetch_repository_metadata_type_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test-owner/test-repo", json=[{"name": "test-repo"}]
    )

    client = GitHubClient()
    with pytest.raises(TypeError):
        client.fetch_repository_metadata("test-owner", "test-repo")


def test_fetch_commit_history_type_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test-owner/test-repo/commits?per_page=100",
        json={"sha": "abc123def456"},
    )

    client = GitHubClient()
    with pytest.raises(TypeError):
        client.fetch_commit_history("test-owner", "test-repo")


def test_github_client_loads_token_from_settings() -> None:
    import src.domain_models.config as config_module

    config_module._settings = None
    os.environ["GITHUB_TOKEN"] = "env-token"  # noqa: S105

    client = GitHubClient()
    assert client.headers["Authorization"] == "token env-token"

    del os.environ["GITHUB_TOKEN"]


def test_get_settings_singleton() -> None:
    # Reset singleton to test initialization
    import src.domain_models.config as config_module

    config_module._settings = None
    os.environ["GITHUB_TOKEN"] = "test-token"  # noqa: S105

    settings = get_settings()
    assert isinstance(settings, Settings)
    assert settings.GITHUB_TOKEN == "test-token"  # noqa: S105

    # Check singleton behavior
    settings_again = get_settings()
    assert settings is settings_again

    del os.environ["GITHUB_TOKEN"]

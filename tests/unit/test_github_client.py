import pytest
from pytest_httpx import HTTPXMock

from src.domain_models import AppConfig
from src.domain_models.exceptions import (
    AuthenticationError,
    GitHubClientError,
    RateLimitError,
    RepositoryNotFoundError,
)
from src.ingestion.github_client import GitHubClient


@pytest.fixture
def github_client() -> GitHubClient:
    config = AppConfig(github_token="fake_token")  # noqa: S106
    return GitHubClient(config)


def test_get_repository_metadata_success(
    github_client: GitHubClient, httpx_mock: HTTPXMock
) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test_owner/test_repo",
        json={
            "name": "test_repo",
            "owner": {"login": "test_owner"},
            "stargazers_count": 100,
            "forks_count": 50,
            "open_issues_count": 10,
        },
    )

    metadata = github_client.get_repository_metadata("test_owner", "test_repo")

    assert metadata.owner == "test_owner"
    assert metadata.repo == "test_repo"
    assert metadata.stargazers_count == 100
    assert metadata.forks_count == 50
    assert metadata.open_issues_count == 10


def test_get_repository_metadata_not_found(
    github_client: GitHubClient, httpx_mock: HTTPXMock
) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test_owner/not_found_repo", status_code=404
    )

    with pytest.raises(RepositoryNotFoundError):
        github_client.get_repository_metadata("test_owner", "not_found_repo")


def test_get_commits_success(github_client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test_owner/test_repo/commits?per_page=100",
        json=[
            {
                "sha": "abc123def",
                "commit": {"author": {"name": "Alice", "date": "2023-11-01T12:00:00Z"}},
            },
            {
                "sha": "def456abc",
                "commit": {"author": {"name": "Bob", "date": "2023-11-02T12:00:00Z"}},
            },
        ],
    )

    commits = github_client.get_commits("test_owner", "test_repo")

    assert len(commits) == 2
    assert commits[0].sha == "abc123def"
    assert commits[0].author_name == "Alice"
    assert commits[1].sha == "def456abc"
    assert commits[1].author_name == "Bob"


def test_github_client_authentication_error(
    github_client: GitHubClient, httpx_mock: HTTPXMock
) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test_owner/test_repo", status_code=401
    )

    with pytest.raises(AuthenticationError):
        github_client.get_repository_metadata("test_owner", "test_repo")


def test_github_client_rate_limit_error(github_client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test_owner/test_repo", status_code=403
    )

    with pytest.raises(RateLimitError):
        github_client.get_repository_metadata("test_owner", "test_repo")


def test_github_client_other_error(github_client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test_owner/test_repo", status_code=500
    )

    with pytest.raises(GitHubClientError):
        github_client.get_repository_metadata("test_owner", "test_repo")

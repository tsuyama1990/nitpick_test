import pytest
from pytest_httpx import HTTPXMock

from src.domain_models import (
    AuthenticationError,
    CommitRecord,
    GitHubAPIError,
    RateLimitError,
    RepositoryMetadata,
    RepositoryNotFoundError,
)
from src.ingestion.github_client import GitHubClient


@pytest.fixture
def client() -> GitHubClient:
    return GitHubClient(token="fake_token")  # noqa: S106


def test_get_repository_metadata_success(client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test/repo",
        json={
            "owner": {"login": "test"},
            "name": "repo",
            "stargazers_count": 100,
            "forks_count": 50,
            "open_issues_count": 10,
        },
    )
    repo = client.get_repository_metadata("test", "repo")
    assert isinstance(repo, RepositoryMetadata)
    assert repo.name == "repo"
    assert repo.owner == "test"
    assert repo.stargazers_count == 100


def test_get_recent_commits_success(client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test/repo/commits?per_page=100",
        json=[
            {
                "sha": "123456",
                "commit": {"author": {"name": "Alice", "date": "2023-01-01T00:00:00Z"}},
            }
        ],
    )
    commits = client.get_recent_commits("test", "repo")
    assert len(commits) == 1
    assert isinstance(commits[0], CommitRecord)
    assert commits[0].sha == "123456"
    assert commits[0].author_name == "Alice"


def test_client_authentication_error(client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url="https://api.github.com/repos/test/repo", status_code=401)
    with pytest.raises(AuthenticationError):
        client.get_repository_metadata("test", "repo")


def test_client_rate_limit_error(client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url="https://api.github.com/repos/test/repo", status_code=429)
    with pytest.raises(RateLimitError):
        client.get_repository_metadata("test", "repo")


def test_client_not_found_error(client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url="https://api.github.com/repos/test/repo", status_code=404)
    with pytest.raises(RepositoryNotFoundError):
        client.get_repository_metadata("test", "repo")


def test_client_other_error(client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url="https://api.github.com/repos/test/repo", status_code=500)
    with pytest.raises(GitHubAPIError):
        client.get_repository_metadata("test", "repo")

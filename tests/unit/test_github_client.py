import httpx
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


def test_fetch_metadata_success(client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/streamlit/streamlit",
        json={
            "owner": {"login": "streamlit"},
            "name": "streamlit",
            "stargazers_count": 100,
            "forks_count": 50,
            "open_issues_count": 10,
        },
    )

    meta = client.fetch_repository_metadata("streamlit/streamlit")
    assert isinstance(meta, RepositoryMetadata)
    assert meta.owner == "streamlit"
    assert meta.name == "streamlit"
    assert meta.stars == 100
    assert meta.forks == 50
    assert meta.open_issues == 10


def test_fetch_metadata_not_found(client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/invalid/repo",
        status_code=404,
    )
    with pytest.raises(RepositoryNotFoundError):
        client.fetch_repository_metadata("invalid/repo")


def test_fetch_commits_success(client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/streamlit/streamlit/commits?per_page=100",
        json=[
            {
                "sha": "abc1234",
                "commit": {"author": {"name": "Alice", "date": "2023-01-01T12:00:00Z"}},
            }
        ],
    )

    commits = client.fetch_latest_commits("streamlit/streamlit")
    assert len(commits) == 1
    assert isinstance(commits[0], CommitRecord)
    assert commits[0].hash == "abc1234"
    assert commits[0].author == "Alice"


def test_auth_error(client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/streamlit/streamlit",
        status_code=401,
        json={"message": "Bad credentials"},
    )
    with pytest.raises(AuthenticationError) as exc_info:
        client.fetch_repository_metadata("streamlit/streamlit")
    assert "fake_token" not in str(exc_info.value)


def test_rate_limit_error(client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/streamlit/streamlit",
        status_code=429,
    )
    with pytest.raises(RateLimitError):
        client.fetch_repository_metadata("streamlit/streamlit")


def test_rate_limit_error_403(client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/streamlit/streamlit",
        status_code=403,
        text="Rate limit exceeded",
    )
    with pytest.raises(RateLimitError):
        client.fetch_repository_metadata("streamlit/streamlit")


def test_general_http_error(client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/streamlit/streamlit",
        status_code=500,
    )
    with pytest.raises(GitHubAPIError, match="GitHub API request failed"):
        client.fetch_repository_metadata("streamlit/streamlit")


def test_network_error_metadata(client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_exception(
        httpx.RequestError("Connection failed"),
        url="https://api.github.com/repos/streamlit/streamlit",
    )
    with pytest.raises(GitHubAPIError, match="Network error while connecting to GitHub"):
        client.fetch_repository_metadata("streamlit/streamlit")


def test_network_error_commits(client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_exception(
        httpx.RequestError("Connection failed"),
        url="https://api.github.com/repos/streamlit/streamlit/commits?per_page=100",
    )
    with pytest.raises(GitHubAPIError, match="Network error while connecting to GitHub"):
        client.fetch_latest_commits("streamlit/streamlit")

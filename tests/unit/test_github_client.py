import pytest
from pytest_httpx import HTTPXMock
from src.ingestion.github_client import GithubClient

from src.config import AppConfig
from src.domain_models import (
    AuthenticationError,
    CommitRecord,
    GitHubAPIError,
    RateLimitError,
    RepositoryMetadata,
    RepositoryNotFoundError,
)


@pytest.fixture
def valid_config() -> AppConfig:
    return AppConfig(github_token="test_token")  # noqa: S106


@pytest.fixture
def client(valid_config: AppConfig) -> GithubClient:
    return GithubClient(config=valid_config)


def test_fetch_repository_metadata_success(client: GithubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/testowner/testrepo",
        json={
            "id": 12345,  # extra field should be ignored or cause validation error depending on setup.
            # Since we use extra="forbid", but we might need to parse only specific fields from raw payload.
            "owner": {"login": "testowner"},
            "name": "testrepo",
            "stargazers_count": 100,
            "forks_count": 50,
            "open_issues_count": 10,
        },
    )

    # Actually Github API returns nested owner, our model just expects "owner": "str"
    # We will need to test how the client transforms the raw data before validation

    # To test properly, let's assume the GithubClient handles this mapping
    # The GithubClient logic will be written to extract the 'login' from 'owner' if it's a dict.

    result = client.fetch_repository_metadata("testowner", "testrepo")
    assert isinstance(result, RepositoryMetadata)
    assert result.name == "testrepo"
    assert result.stargazers_count == 100


def test_fetch_repository_metadata_not_found(client: GithubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url="https://api.github.com/repos/testowner/testrepo", status_code=404)
    with pytest.raises(RepositoryNotFoundError):
        client.fetch_repository_metadata("testowner", "testrepo")


def test_fetch_latest_commits_success(client: GithubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/testowner/testrepo/commits?per_page=1",
        json=[
            {
                "sha": "abcdef123456",
                "commit": {"author": {"name": "Test Author", "date": "2023-10-01T12:00:00Z"}},
            }
        ],
    )
    result = client.fetch_latest_commits("testowner", "testrepo", limit=1)
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], CommitRecord)
    assert result[0].sha == "abcdef123456"


def test_client_authentication_error(client: GithubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url="https://api.github.com/repos/testowner/testrepo", status_code=401)
    with pytest.raises(AuthenticationError) as exc_info:
        client.fetch_repository_metadata("testowner", "testrepo")

    assert "test_token" not in str(exc_info.value)


def test_client_rate_limit_error(client: GithubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/testowner/testrepo",
        status_code=403,
        headers={"X-RateLimit-Remaining": "0"},
    )
    with pytest.raises(RateLimitError):
        client.fetch_repository_metadata("testowner", "testrepo")


def test_client_generic_error(client: GithubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url="https://api.github.com/repos/testowner/testrepo", status_code=500)
    with pytest.raises(GitHubAPIError):
        client.fetch_repository_metadata("testowner", "testrepo")

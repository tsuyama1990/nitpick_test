import httpx
import pytest
from pytest_httpx import HTTPXMock

from src.domain_models import (
    AuthenticationError,
    GitHubClientError,
    RateLimitError,
    RepositoryNotFoundError,
)
from src.ingestion import GitHubClient


@pytest.fixture
def github_client() -> GitHubClient:
    return GitHubClient(token="fake_test_token")  # noqa: S106

def test_get_repository_metadata_success(github_client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    mock_data = {
        "owner": {"login": "testowner"},
        "name": "testrepo",
        "stargazers_count": 100,
        "forks_count": 50,
        "open_issues_count": 5
    }
    httpx_mock.add_response(json=mock_data)

    metadata = github_client.get_repository_metadata("testowner", "testrepo")

    assert metadata.owner == "testowner"
    assert metadata.repo_name == "testrepo"
    assert metadata.star_count == 100

def test_get_commits_success(github_client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    mock_data = [
        {
            "sha": "abcdef",
            "commit": {
                "author": {
                    "name": "Test Author",
                    "date": "2023-10-10T10:00:00Z"
                }
            }
        }
    ]
    httpx_mock.add_response(json=mock_data)

    commits = github_client.get_commits("testowner", "testrepo", limit=1)

    assert len(commits) == 1
    assert commits[0].sha == "abcdef"
    assert commits[0].author_name == "Test Author"

def test_auth_error(github_client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(status_code=401)

    with pytest.raises(AuthenticationError, match="Invalid authentication credentials."):
        github_client.get_repository_metadata("testowner", "testrepo")

def test_not_found_error(github_client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(status_code=404)

    with pytest.raises(RepositoryNotFoundError, match="Repository not found."):
        github_client.get_repository_metadata("testowner", "testrepo")

def test_rate_limit_error(github_client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(status_code=429)

    with pytest.raises(RateLimitError, match="GitHub API rate limit exceeded."):
        github_client.get_repository_metadata("testowner", "testrepo")

def test_request_error(github_client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_exception(httpx.ReadTimeout("Timeout"))

    with pytest.raises(GitHubClientError, match="Request failed"):
        github_client.get_repository_metadata("testowner", "testrepo")

def test_invalid_json_validation_error_metadata(github_client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(json={"invalid": "data"})

    with pytest.raises(GitHubClientError, match="Invalid repository metadata response"):
        github_client.get_repository_metadata("testowner", "testrepo")

def test_invalid_json_validation_error_commits(github_client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(json=[{"invalid": "data"}])

    with pytest.raises(GitHubClientError, match="Invalid commit record response"):
        github_client.get_commits("testowner", "testrepo")

def test_request_error_commits(github_client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_exception(httpx.ReadTimeout("Timeout"))

    with pytest.raises(GitHubClientError, match="Request failed"):
        github_client.get_commits("testowner", "testrepo")

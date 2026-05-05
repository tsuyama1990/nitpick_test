import httpx
import pytest
from pytest_httpx import HTTPXMock

from src.domain_models.exceptions import GitHubAPIError, RateLimitError, RepositoryNotFoundError
from src.ingestion.github_client import fetch_commits, fetch_repo_metadata


def test_fetch_repo_metadata_success(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test/repo",
        json={"stargazers_count": 10, "forks_count": 5, "open_issues_count": 2}
    )
    result = fetch_repo_metadata("test/repo")
    assert result.stargazers_count == 10

def test_fetch_repo_metadata_not_found(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url="https://api.github.com/repos/test/repo", status_code=404)
    with pytest.raises(RepositoryNotFoundError):
        fetch_repo_metadata("test/repo")

def test_fetch_commits_success(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test/repo/commits?per_page=100",
        json=[
            {
                "commit": {
                    "author": {"name": "Alice", "date": "2023-01-01T12:00:00Z"},
                    "message": "Init"
                }
            }
        ]
    )
    result = fetch_commits("test/repo")
    assert len(result) == 1
    assert result[0].author_name == "Alice"

def test_fetch_rate_limit(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url="https://api.github.com/repos/test/repo", status_code=403)
    with pytest.raises(RateLimitError):
        fetch_repo_metadata("test/repo")

def test_fetch_commits_network_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_exception(httpx.RequestError("Network Error"))
    with pytest.raises(GitHubAPIError):
        fetch_commits("test/repo")

def test_fetch_metadata_network_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_exception(httpx.RequestError("Network Error"))
    with pytest.raises(GitHubAPIError):
        fetch_repo_metadata("test/repo")

def test_fetch_http_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url="https://api.github.com/repos/test/repo", status_code=500)
    with pytest.raises(GitHubAPIError):
        fetch_repo_metadata("test/repo")

import httpx
import pytest

try:
    from datetime import UTC, datetime
except ImportError:
    from datetime import datetime, timezone  # noqa: F401
    UTC = timezone.utc

import pytest_httpx
from src.domain_models import (
    AuthenticationError,
    RateLimitError,
    RepositoryNotFoundError,
    RepositoryMetadata,
    CommitRecord,
    DomainError,
)
from src.ingestion.github_client import GitHubClient

def test_github_client_missing_token() -> None:
    with pytest.raises(AuthenticationError, match="GitHub token must be provided."):
        GitHubClient(token="")

def test_get_repository_metadata_success(httpx_mock: pytest_httpx.HTTPXMock) -> None:
    client = GitHubClient(token="dummy_token")  # noqa: S106

    mock_response = {
        "name": "streamlit",
        "owner": {"login": "streamlit"},
        "stargazers_count": 100,
        "forks_count": 50,
        "open_issues_count": 10,
    }
    httpx_mock.add_response(
        url="https://api.github.com/repos/streamlit/streamlit", json=mock_response
    )

    result = client.get_repository_metadata("streamlit/streamlit")
    assert isinstance(result, RepositoryMetadata)
    assert result.repo_name == "streamlit"
    assert result.owner == "streamlit"
    assert result.star_count == 100
    assert result.fork_count == 50
    assert result.open_issue_count == 10

def test_get_recent_commits_success(httpx_mock: pytest_httpx.HTTPXMock) -> None:
    client = GitHubClient(token="dummy_token")  # noqa: S106

    mock_response = [
        {
            "sha": "abcdef123456",
            "commit": {"author": {"name": "John Doe", "date": "2023-10-01T12:00:00Z"}},
        }
    ]
    httpx_mock.add_response(
        url="https://api.github.com/repos/streamlit/streamlit/commits?per_page=100",
        json=mock_response,
    )

    result = client.get_recent_commits("streamlit/streamlit")
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], CommitRecord)
    assert result[0].commit_hash == "abcdef123456"
    assert result[0].author_name == "John Doe"
    assert result[0].timestamp == datetime(2023, 10, 1, 12, 0, 0, tzinfo=UTC)

def test_github_client_auth_error(httpx_mock: pytest_httpx.HTTPXMock) -> None:
    client = GitHubClient(token="invalid_token")  # noqa: S106

    httpx_mock.add_response(
        url="https://api.github.com/repos/streamlit/streamlit",
        status_code=401,
        json={"message": "Bad credentials"},
    )

    with pytest.raises(AuthenticationError) as exc_info:
        client.get_repository_metadata("streamlit/streamlit")

    # Ensure token is not in the error message
    assert "invalid_token" not in str(exc_info.value)
    assert "401" in str(exc_info.value) or "unauthorized" in str(exc_info.value).lower()

def test_github_client_rate_limit_error(httpx_mock: pytest_httpx.HTTPXMock) -> None:
    client = GitHubClient(token="dummy_token")  # noqa: S106

    httpx_mock.add_response(
        url="https://api.github.com/repos/streamlit/streamlit",
        status_code=429,
        json={"message": "API rate limit exceeded"},
    )

    with pytest.raises(RateLimitError):
        client.get_repository_metadata("streamlit/streamlit")

def test_github_client_forbidden_error(httpx_mock: pytest_httpx.HTTPXMock) -> None:
    client = GitHubClient(token="dummy_token")  # noqa: S106

    httpx_mock.add_response(
        url="https://api.github.com/repos/streamlit/streamlit",
        status_code=403,
        json={"message": "API rate limit exceeded"},  # 403 can also be rate limit
    )

    # We map 403 to RateLimitError (or generic Authentication depending on context, we choose RateLimit based on standard GH API behaviour for missing token rate limits)
    with pytest.raises(RateLimitError):
        client.get_repository_metadata("streamlit/streamlit")

def test_github_client_not_found_error(httpx_mock: pytest_httpx.HTTPXMock) -> None:
    client = GitHubClient(token="dummy_token")  # noqa: S106

    httpx_mock.add_response(
        url="https://api.github.com/repos/invalid/repo", status_code=404, json={"message": "Not Found"}
    )

    with pytest.raises(RepositoryNotFoundError):
        client.get_repository_metadata("invalid/repo")

def test_github_client_general_error(httpx_mock: pytest_httpx.HTTPXMock) -> None:
    client = GitHubClient(token="dummy_token")  # noqa: S106

    httpx_mock.add_response(
        url="https://api.github.com/repos/invalid/repo",
        status_code=500,
        json={"message": "Internal Server Error"},
    )

    with pytest.raises(DomainError):
        client.get_repository_metadata("invalid/repo")

def test_github_client_request_error(httpx_mock: pytest_httpx.HTTPXMock) -> None:
    client = GitHubClient(token="dummy_token")  # noqa: S106

    httpx_mock.add_exception(
        httpx.RequestError(
            "Network error",
            request=httpx.Request("GET", "https://api.github.com/repos/invalid/repo"),
        ),
        url="https://api.github.com/repos/invalid/repo",
    )

    with pytest.raises(DomainError):
        client.get_repository_metadata("invalid/repo")

def test_github_client_commit_request_error(httpx_mock: pytest_httpx.HTTPXMock) -> None:
    client = GitHubClient(token="dummy_token")  # noqa: S106

    httpx_mock.add_exception(
        httpx.RequestError(
            "Network error",
            request=httpx.Request("GET", "https://api.github.com/repos/invalid/repo/commits"),
        ),
        url="https://api.github.com/repos/invalid/repo/commits?per_page=100",
    )

    with pytest.raises(DomainError):
        client.get_recent_commits("invalid/repo")

def test_github_client_commit_response_format_error(httpx_mock: pytest_httpx.HTTPXMock) -> None:
    client = GitHubClient(token="dummy_token")  # noqa: S106

    httpx_mock.add_response(
        url="https://api.github.com/repos/streamlit/streamlit/commits?per_page=100",
        json={"message": "Not a list"},  # unexpected format
    )

    with pytest.raises(DomainError):
        client.get_recent_commits("streamlit/streamlit")

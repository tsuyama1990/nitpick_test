import pytest
from pytest_httpx import HTTPXMock

from src.domain_models.exceptions import (
    AuthenticationError,
    RateLimitError,
    RepositoryNotFoundError,
)
from src.domain_models.models import CommitRecord, RepositoryMetadata
from src.ingestion.github_client import GithubClient


def test_get_repository_metadata_success(
    httpx_mock: HTTPXMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "dummy_token")
    client = GithubClient()
    httpx_mock.add_response(
        url="https://api.github.com/repos/streamlit/streamlit",
        json={
            "owner": {"login": "streamlit"},
            "name": "streamlit",
            "stargazers_count": 100,
            "forks_count": 10,
            "open_issues_count": 5,
        },
    )
    result = client.get_repository_metadata("streamlit", "streamlit")
    assert isinstance(result, RepositoryMetadata)
    assert result.owner == "streamlit"
    assert result.repo == "streamlit"
    assert result.star_count == 100
    assert result.fork_count == 10
    assert result.open_issue_count == 5


def test_get_repository_metadata_not_found(
    httpx_mock: HTTPXMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "dummy_token")
    client = GithubClient()
    httpx_mock.add_response(
        url="https://api.github.com/repos/invalid/invalid",
        status_code=404,
        json={"message": "Not Found"},
    )
    with pytest.raises(RepositoryNotFoundError):
        client.get_repository_metadata("invalid", "invalid")


def test_get_repository_metadata_unauthorized(
    httpx_mock: HTTPXMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "dummy_token")
    client = GithubClient()
    httpx_mock.add_response(
        url="https://api.github.com/repos/streamlit/streamlit",
        status_code=401,
        json={"message": "Bad credentials"},
    )
    with pytest.raises(AuthenticationError) as exc_info:
        client.get_repository_metadata("streamlit", "streamlit")
    assert "dummy_token" not in str(exc_info.value)  # Ensure token isn't leaked


def test_get_repository_metadata_rate_limit(
    httpx_mock: HTTPXMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "dummy_token")
    client = GithubClient()
    httpx_mock.add_response(
        url="https://api.github.com/repos/streamlit/streamlit",
        status_code=403,
        headers={"X-RateLimit-Remaining": "0"},
        json={"message": "API rate limit exceeded"},
    )
    with pytest.raises(RateLimitError):
        client.get_repository_metadata("streamlit", "streamlit")


def test_get_repository_metadata_rate_limit_429(
    httpx_mock: HTTPXMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "dummy_token")
    client = GithubClient()
    httpx_mock.add_response(
        url="https://api.github.com/repos/streamlit/streamlit",
        status_code=429,
        json={"message": "Too Many Requests"},
    )
    with pytest.raises(RateLimitError):
        client.get_repository_metadata("streamlit", "streamlit")


def test_get_recent_commits_success(httpx_mock: HTTPXMock, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "dummy_token")
    client = GithubClient()
    httpx_mock.add_response(
        url="https://api.github.com/repos/streamlit/streamlit/commits?per_page=2",
        json=[
            {
                "sha": "abc1234",
                "commit": {"author": {"name": "Author One", "date": "2023-10-10T10:10:10Z"}},
            },
            {
                "sha": "def5678",
                "commit": {"author": {"name": "Author Two", "date": "2023-10-10T10:11:10Z"}},
            },
        ],
    )
    results = client.get_recent_commits("streamlit", "streamlit", limit=2)
    assert len(results) == 2
    assert isinstance(results[0], CommitRecord)
    assert results[0].commit_hash == "abc1234"
    assert results[0].author_name == "Author One"
    assert results[1].commit_hash == "def5678"
    assert results[1].author_name == "Author Two"

import os
from collections.abc import Generator
from unittest.mock import patch

import httpx
import pytest
from pytest_httpx import HTTPXMock

from src.domain_models.github import CommitDetail, RepositoryInfo
from src.ingestion.github_client import fetch_recent_commits, fetch_repo_info


@pytest.fixture(autouse=True)
def _mock_env() -> Generator[None, None, None]:
    """Mock the environment variables for testing."""
    with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token_123"}):
        yield


def test_fetch_repo_info_success(httpx_mock: HTTPXMock) -> None:
    mock_response = {
        "full_name": "owner/repo",
        "stargazers_count": 100,
        "forks_count": 50,
        "open_issues_count": 10,
    }
    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/repo",
        json=mock_response,
        status_code=200,
    )

    repo_info = fetch_repo_info("owner", "repo")

    assert isinstance(repo_info, RepositoryInfo)
    assert repo_info.name == "owner/repo"
    assert repo_info.stars == 100


def test_fetch_recent_commits_success(httpx_mock: HTTPXMock) -> None:
    mock_response = [
        {
            "sha": "1234567890abcdef",
            "commit": {
                "author": {
                    "name": "Test User",
                    "date": "2023-01-01T12:00:00Z",
                },
                "message": "Initial commit",
            },
        }
    ]
    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/repo/commits?per_page=100",
        json=mock_response,
        status_code=200,
    )

    commits = fetch_recent_commits("owner", "repo")

    assert len(commits) == 1
    assert isinstance(commits[0], CommitDetail)
    assert commits[0].sha == "1234567890abcdef"


def test_fetch_repo_info_403(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/repo",
        status_code=403,
        text="Rate limit exceeded",
    )

    with pytest.raises(PermissionError, match="GitHub API Error 403"):
        fetch_repo_info("owner", "repo")


def test_fetch_repo_info_429(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/repo",
        status_code=429,
        text="Too many requests",
    )

    with pytest.raises(PermissionError, match="GitHub API Error 429"):
        fetch_repo_info("owner", "repo")


def test_fetch_repo_info_other_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/repo",
        status_code=404,
        text="Not Found",
    )

    with pytest.raises(httpx.HTTPStatusError):
        fetch_repo_info("owner", "repo")


def test_fetch_repo_info_invalid_response(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/repo",
        json=["not", "a", "dict"],
        status_code=200,
    )

    with pytest.raises(TypeError, match="Expected dict"):
        fetch_repo_info("owner", "repo")


def test_fetch_recent_commits_invalid_response(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/repo/commits?per_page=100",
        json={"not": "a list"},
        status_code=200,
    )

    with pytest.raises(TypeError, match="Expected list"):
        fetch_recent_commits("owner", "repo")

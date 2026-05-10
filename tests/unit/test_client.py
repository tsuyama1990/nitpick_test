from collections.abc import Generator
from unittest.mock import patch

import pytest
from pytest_httpx import HTTPXMock

from src.ingestion.client import GitHubAPIError, GitHubClient


@pytest.fixture
def mock_settings() -> Generator[None, None, None]:
    with patch.dict("os.environ", {"GITHUB_TOKEN": "fake_token"}):
        yield


def test_get_repo_info_success(httpx_mock: HTTPXMock, mock_settings: None) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test-owner/test-repo",
        json={
            "stargazers_count": 100,
            "forks_count": 50,
            "open_issues_count": 10,
            "extra": "ignore",
        },
    )
    client = GitHubClient()
    repo_info = client.get_repo_info("test-owner", "test-repo")

    assert repo_info.stargazers_count == 100
    assert repo_info.forks_count == 50
    assert repo_info.open_issues_count == 10


def test_get_repo_info_404(httpx_mock: HTTPXMock, mock_settings: None) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test-owner/test-repo", status_code=404
    )
    client = GitHubClient()
    with pytest.raises(GitHubAPIError, match="Repository not found."):
        client.get_repo_info("test-owner", "test-repo")


def test_get_repo_info_403(httpx_mock: HTTPXMock, mock_settings: None) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test-owner/test-repo", status_code=403
    )
    client = GitHubClient()
    with pytest.raises(GitHubAPIError, match="Rate limit exceeded or access forbidden."):
        client.get_repo_info("test-owner", "test-repo")


def test_get_recent_commits_success(httpx_mock: HTTPXMock, mock_settings: None) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test-owner/test-repo/commits?per_page=100",
        json=[
            {
                "sha": "123",
                "commit": {
                    "committer": {"name": "Alice", "date": "2023-01-01T12:00:00Z"},
                    "message": "init",
                },
            }
        ],
    )
    client = GitHubClient()
    commits = client.get_recent_commits("test-owner", "test-repo")

    assert len(commits) == 1
    assert commits[0].sha == "123"
    assert commits[0].commit.committer.name == "Alice"

from collections.abc import Generator
from unittest.mock import patch

import pytest
from pytest_httpx import HTTPXMock

from src.ingestion import GitHubClient, GitHubClientError


@pytest.fixture
def mock_settings() -> Generator[None, None, None]:
    with patch("src.ingestion.get_settings") as mock:
        mock.return_value.GITHUB_TOKEN = "dummy_token"  # noqa: S105
        yield


def test_get_repository_info_success(httpx_mock: HTTPXMock, mock_settings: None) -> None:
    client = GitHubClient()
    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/repo",
        json={
            "stargazers_count": 100,
            "forks_count": 50,
            "open_issues_count": 10,
        },
    )
    repo_info = client.get_repository_info("owner", "repo")
    assert repo_info.stargazers_count == 100
    assert repo_info.forks_count == 50
    assert repo_info.open_issues_count == 10


def test_get_commits_success(httpx_mock: HTTPXMock, mock_settings: None) -> None:
    client = GitHubClient()
    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/repo/commits?per_page=100",
        json=[
            {
                "commit": {
                    "author": {"name": "Alice", "date": "2023-01-01T12:00:00Z"},
                }
            },
            {
                "commit": {
                    "author": {"name": "Bob", "date": "2023-01-02T12:00:00Z"},
                }
            },
        ],
    )
    commits = client.get_commits("owner", "repo")
    assert len(commits) == 2
    assert commits[0].commit.author.name == "Alice"
    assert commits[1].commit.author.name == "Bob"


def test_get_repository_info_404(httpx_mock: HTTPXMock, mock_settings: None) -> None:
    client = GitHubClient()
    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/invalid-repo",
        status_code=404,
    )
    with pytest.raises(GitHubClientError, match="リポジトリが見つかりません"):
        client.get_repository_info("owner", "invalid-repo")


def test_get_repository_info_403(httpx_mock: HTTPXMock, mock_settings: None) -> None:
    client = GitHubClient()
    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/repo",
        status_code=403,
    )
    with pytest.raises(GitHubClientError, match="認証エラーが発生しました"):
        client.get_repository_info("owner", "repo")

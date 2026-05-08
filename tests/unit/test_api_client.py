from unittest.mock import patch

import pytest
from pytest_httpx import HTTPXMock

from src.ingestion.api_client import GitHubAPIClient


def test_get_repo_info_success(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test-owner/test-repo",
        json={"stargazers_count": 100, "forks_count": 50, "open_issues_count": 10},
    )
    with patch("src.ingestion.api_client.get_settings") as mock_settings:
        mock_settings.return_value.GITHUB_TOKEN = "dummy_token"  # noqa: S105
        client = GitHubAPIClient()
        repo_info = client.get_repo_info("test-owner", "test-repo")

        assert repo_info.stargazers_count == 100
        assert repo_info.forks_count == 50
        assert repo_info.open_issues_count == 10


def test_get_recent_commits_success(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test-owner/test-repo/commits?per_page=2",
        json=[
            {
                "sha": "abc",
                "commit": {"committer": {"name": "User 1", "date": "2023-01-01T10:00:00Z"}},
            },
            {
                "sha": "def",
                "commit": {"committer": {"name": "User 2", "date": "2023-01-02T10:00:00Z"}},
            },
        ],
    )
    with patch("src.ingestion.api_client.get_settings") as mock_settings:
        mock_settings.return_value.GITHUB_TOKEN = "dummy_token"  # noqa: S105
        client = GitHubAPIClient()
        commits = client.get_recent_commits("test-owner", "test-repo", limit=2)

        assert len(commits) == 2
        assert commits[0].sha == "abc"
        assert commits[0].committer_name == "User 1"
        assert commits[1].sha == "def"
        assert commits[1].committer_name == "User 2"


def test_handle_rate_limit(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(status_code=429)
    with patch("src.ingestion.api_client.get_settings") as mock_settings:
        mock_settings.return_value.GITHUB_TOKEN = "dummy_token"  # noqa: S105
        client = GitHubAPIClient()
        with pytest.raises(RuntimeError, match="429"):
            client.get_repo_info("test-owner", "test-repo")


def test_handle_not_found(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(status_code=404)
    with patch("src.ingestion.api_client.get_settings") as mock_settings:
        mock_settings.return_value.GITHUB_TOKEN = "dummy_token"  # noqa: S105
        client = GitHubAPIClient()
        with pytest.raises(RuntimeError, match="404"):
            client.get_repo_info("test-owner", "test-repo")

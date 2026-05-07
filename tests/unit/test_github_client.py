import logging
from unittest.mock import patch

import pytest
from pytest_httpx import HTTPXMock

from src.ingestion import GitHubClient


@pytest.fixture
def mock_env_token() -> None:
    # Set a fake token in environment safely via patch
    with patch("src.config.settings.Settings.model_validate", return_value=None):
        pass


def test_github_client_headers(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "fake_test_token")
    client = GitHubClient()
    assert client.headers["Authorization"] == "token fake_test_token"
    assert client.headers["Accept"] == "application/vnd.github.v3+json"


def test_fetch_repository_info_success(
    monkeypatch: pytest.MonkeyPatch, httpx_mock: HTTPXMock
) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "fake_test_token")
    client = GitHubClient()

    mock_response = {
        "stargazers_count": 1500,
        "forks_count": 300,
        "open_issues_count": 42,
        "name": "test-repo",
        "description": "A test repo",
    }
    httpx_mock.add_response(
        url="https://api.github.com/repos/test-owner/test-repo", json=mock_response, status_code=200
    )

    repo_info = client.fetch_repository_info("test-owner", "test-repo")

    assert repo_info.stargazers_count == 1500
    assert repo_info.forks_count == 300
    assert repo_info.open_issues_count == 42

    # Ensure no external call was made unmocked
    request = httpx_mock.get_request()
    assert request is not None
    assert request.headers["authorization"] == "token fake_test_token"


def test_fetch_recent_commits_success(
    monkeypatch: pytest.MonkeyPatch, httpx_mock: HTTPXMock
) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "fake_test_token")
    client = GitHubClient()

    mock_response = [
        {
            "sha": "12345",
            "commit": {
                "author": {"name": "Alice", "date": "2023-10-01T10:00:00Z"},
                "message": "Update docs",
            },
        },
        {
            "sha": "67890",
            "commit": {
                "author": {"name": "Bob", "date": "2023-10-02T11:00:00Z"},
                "message": "Fix bug",
            },
        },
    ]
    httpx_mock.add_response(
        url="https://api.github.com/repos/test-owner/test-repo/commits?per_page=2",
        json=mock_response,
        status_code=200,
    )

    commits = client.fetch_recent_commits("test-owner", "test-repo", limit=2)

    assert len(commits) == 2
    assert commits[0].author_name == "Alice"
    assert commits[0].date.year == 2023
    assert commits[1].author_name == "Bob"


def test_logger_level_configuration() -> None:
    # Ensure httpx logger is set to WARNING to avoid leaking sensitive headers
    httpx_logger = logging.getLogger("httpx")
    assert httpx_logger.level >= logging.WARNING

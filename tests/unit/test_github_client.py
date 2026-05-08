"""Unit tests for GitHub API client."""

import httpx
import pytest
from pytest_httpx import HTTPXMock

from src.ingestion.github_client import _get_headers, get_repo_commits, get_repo_info


@pytest.fixture
def mock_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock the settings to provide a dummy token."""
    monkeypatch.setenv("GITHUB_TOKEN", "dummy_token_123")


def test_get_headers(mock_settings: None) -> None:
    """Test header generation."""
    headers = _get_headers()
    assert headers["Accept"] == "application/vnd.github.v3+json"
    assert headers["Authorization"] == "token dummy_token_123"
    assert headers["X-GitHub-Api-Version"] == "2022-11-28"


def test_get_repo_info_success(httpx_mock: HTTPXMock, mock_settings: None) -> None:
    """Test successful repo info fetch."""
    mock_data = {"stargazers_count": 100, "forks_count": 50, "open_issues_count": 5}
    httpx_mock.add_response(
        url="https://api.github.com/repos/test_owner/test_repo", json=mock_data, status_code=200
    )
    result = get_repo_info("test_owner", "test_repo")
    assert result == mock_data


def test_get_repo_commits_success(httpx_mock: HTTPXMock, mock_settings: None) -> None:
    """Test successful commit history fetch."""
    mock_data = [
        {"commit": {"author": {"name": "Test User", "date": "2023-01-01"}}},
        {"commit": {"author": {"name": "Test User 2", "date": "2023-01-02"}}},
    ]
    httpx_mock.add_response(
        url="https://api.github.com/repos/test_owner/test_repo/commits?per_page=100",
        json=mock_data,
        status_code=200,
    )
    result = get_repo_commits("test_owner", "test_repo")
    assert len(result) == 2
    assert result == mock_data


def test_get_repo_info_403(httpx_mock: HTTPXMock, mock_settings: None) -> None:
    """Test 403 Forbidden handling."""
    httpx_mock.add_response(
        url="https://api.github.com/repos/test_owner/test_repo",
        status_code=403,
        text="Rate limit exceeded",
    )
    with pytest.raises(PermissionError, match="403 Forbidden"):
        get_repo_info("test_owner", "test_repo")


def test_get_repo_info_429(httpx_mock: HTTPXMock, mock_settings: None) -> None:
    """Test 429 Too Many Requests handling."""
    httpx_mock.add_response(
        url="https://api.github.com/repos/test_owner/test_repo",
        status_code=429,
        text="Too many requests",
    )
    with pytest.raises(ConnectionError, match="429 Too Many Requests"):
        get_repo_info("test_owner", "test_repo")


def test_get_repo_info_404(httpx_mock: HTTPXMock, mock_settings: None) -> None:
    """Test 404 Not Found handling."""
    httpx_mock.add_response(
        url="https://api.github.com/repos/test_owner/test_repo", status_code=404, text="Not Found"
    )
    with pytest.raises(ValueError, match="404 Not Found"):
        get_repo_info("test_owner", "test_repo")


def test_get_repo_info_other_error(httpx_mock: HTTPXMock, mock_settings: None) -> None:
    """Test other HTTP errors."""
    httpx_mock.add_response(
        url="https://api.github.com/repos/test_owner/test_repo",
        status_code=500,
        text="Internal Server Error",
    )
    with pytest.raises(httpx.HTTPStatusError):
        get_repo_info("test_owner", "test_repo")


@pytest.mark.live
def test_live_get_repo_info() -> None:
    """Live API test for public repo (should not be executed in normal runs due to -m 'not live')."""
    import os

    if not os.getenv("GITHUB_TOKEN"):
        pytest.skip("No GITHUB_TOKEN set for live tests")

    repo_info = get_repo_info("streamlit", "streamlit")
    assert "stargazers_count" in repo_info
    assert repo_info["stargazers_count"] > 0
    assert "forks_count" in repo_info
    assert "open_issues_count" in repo_info


@pytest.mark.live
def test_live_get_repo_commits() -> None:
    """Live API test for public repo commits."""
    import os

    if not os.getenv("GITHUB_TOKEN"):
        pytest.skip("No GITHUB_TOKEN set for live tests")

    commits = get_repo_commits("streamlit", "streamlit", per_page=5)
    assert len(commits) == 5
    assert "commit" in commits[0]

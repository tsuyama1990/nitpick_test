from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from pytest_httpx import HTTPXMock

from src.github_client import AuthError, GitHubClient, NotFoundError, RateLimitError


@pytest.fixture
def mock_settings() -> Generator[MagicMock, None, None]:
    with patch("src.github_client.get_settings") as mock_get_settings:
        mock_get_settings.return_value.GITHUB_TOKEN = "dummy"  # noqa: S105
        yield mock_get_settings


def test_get_repo_metrics_success(httpx_mock: HTTPXMock, mock_settings: MagicMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/repo",
        json={"stargazers_count": 10, "forks_count": 5, "open_issues_count": 2, "extra": "field"},
    )
    res = GitHubClient().get_repo_metrics("owner", "repo")
    assert res["stargazers_count"] == 10
    assert "extra" not in res


def test_get_commits_success(httpx_mock: HTTPXMock, mock_settings: MagicMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/repo/commits?per_page=100",
        json=[
            {"commit": {"author": {"name": "Alice", "date": "2023-01-01T12:00:00Z"}}, "sha": "1"}
        ],
    )
    res = GitHubClient().get_commits("owner", "repo")
    assert res[0]["name"] == "Alice"
    assert "sha" not in res[0]


def test_github_client_errors(httpx_mock: HTTPXMock, mock_settings: MagicMock) -> None:
    c = GitHubClient()
    httpx_mock.add_response(url="https://api.github.com/repos/o/r404", status_code=404)
    with pytest.raises(NotFoundError):
        c.get_repo_metrics("o", "r404")

    httpx_mock.add_response(url="https://api.github.com/repos/o/r403", status_code=403)
    with pytest.raises(RateLimitError):
        c.get_repo_metrics("o", "r403")

    httpx_mock.add_response(url="https://api.github.com/repos/o/r401", status_code=401)
    with pytest.raises(AuthError):
        c.get_repo_metrics("o", "r401")

    httpx_mock.add_response(url="https://api.github.com/repos/o/rt1", json=[])
    with pytest.raises(TypeError):
        c.get_repo_metrics("o", "rt1")

    httpx_mock.add_response(url="https://api.github.com/repos/o/rt2/commits?per_page=100", json={})
    with pytest.raises(TypeError):
        c.get_commits("o", "rt2")

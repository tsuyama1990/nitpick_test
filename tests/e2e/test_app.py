from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from pytest_httpx import HTTPXMock

from src.dashboard_service import DashboardService
from src.github_client import AuthError, RateLimitError


@pytest.fixture
def mock_settings() -> Generator[MagicMock, None, None]:
    with patch("src.github_client.get_settings") as mock_get_settings:
        mock_get_settings.return_value.GITHUB_TOKEN = "dummy"  # noqa: S105
        yield mock_get_settings


def test_dashboard_service_e2e_mocked(httpx_mock: HTTPXMock, mock_settings: MagicMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/o/r",
        json={"stargazers_count": 100, "forks_count": 50, "open_issues_count": 10},
    )
    httpx_mock.add_response(
        url="https://api.github.com/repos/o/r/commits?per_page=100",
        json=[{"commit": {"author": {"name": "A", "date": "2023-01-01T12:00:00Z"}}}],
    )
    s = DashboardService()
    s.cache.clear("o_r_commits_by_date")
    s.cache.clear("o_r_top_committers")
    m = s.get_repo_metrics("o", "r")
    assert m["stargazers_count"] == 100
    d1, d2 = s.get_commit_data("o", "r")
    assert d1.shape == (1, 2)


@pytest.mark.live
def test_dashboard_service_e2e_live() -> None:
    s = DashboardService()
    try:
        m = s.get_repo_metrics("tiangolo", "fastapi")
        assert m["stargazers_count"] > 1000
    except (RateLimitError, AuthError):
        pytest.skip("Rate limit or auth")

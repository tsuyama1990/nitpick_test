from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from pytest_httpx import HTTPXMock

import src.config
from src.dashboard_service import DashboardService
from src.github_client import AuthError, RateLimitError


@pytest.fixture(autouse=True)
def _reset_singleton() -> Generator[None, None, None]:
    """Reset the singleton instance before and after each test."""
    src.config._settings = None
    yield
    src.config._settings = None


@pytest.fixture
def mock_settings() -> Generator[MagicMock, None, None]:
    with patch("src.config.Settings") as mock_settings_class:
        mock_instance = MagicMock()
        mock_instance.GITHUB_TOKEN = "dummy"  # noqa: S105
        mock_instance.GITHUB_API_URL = "https://api.github.com"
        mock_instance.HTTP_TIMEOUT = 10.0
        mock_instance.CACHE_TTL_SECONDS = 3600
        mock_instance.CACHE_DIR = None
        mock_settings_class.return_value = mock_instance
        yield mock_instance


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

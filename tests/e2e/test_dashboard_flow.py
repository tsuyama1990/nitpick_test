import os
import tempfile

from pytest_httpx import HTTPXMock

from src.config.settings import Settings
from src.services.dashboard_controller import DashboardController


def test_dashboard_controller_e2e(mock_settings: Settings, httpx_mock: HTTPXMock) -> None:
    # First call gets metrics
    httpx_mock.add_response(
        url="https://api.github.com/repos/test/repo",
        json={"stargazers_count": 1000, "forks_count": 500, "open_issues_count": 20},
    )
    # First call also gets commits because of cache miss
    httpx_mock.add_response(
        url="https://api.github.com/repos/test/repo/commits?per_page=100",
        json=[
            {"commit": {"author": {"name": "UserA", "date": "2023-10-01T10:00:00Z"}}},
            {"commit": {"author": {"name": "UserA", "date": "2023-10-01T11:00:00Z"}}},
            {"commit": {"author": {"name": "UserB", "date": "2023-10-02T10:00:00Z"}}}
        ]
    )
    os.environ["CACHE_DIR"] = tempfile.mkdtemp()
    controller = DashboardController()

    data1 = controller.get_dashboard_data("test", "repo")

    assert data1.metrics.stars == 1000
    assert len(data1.daily_commits) == 2
    assert len(data1.top_committers) == 2

    # second call should hit cache for both commits and metrics
    data2 = controller.get_dashboard_data("test", "repo")

    assert len(data2.daily_commits) == 2
    assert httpx_mock.get_requests()[0].url == "https://api.github.com/repos/test/repo"
    assert httpx_mock.get_requests()[1].url == "https://api.github.com/repos/test/repo/commits?per_page=100"
    # Exact length should be 2 because the second run uses the cache manager
    assert len(httpx_mock.get_requests()) == 2

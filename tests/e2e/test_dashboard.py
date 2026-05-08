"""E2E test for dashboard orchestration."""

import pytest
from pytest_httpx import HTTPXMock

from src.presentation import get_dashboard_data


@pytest.fixture
def mock_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock the settings to provide a dummy token."""
    monkeypatch.setenv("GITHUB_TOKEN", "dummy_token_123")


def test_full_cycle(
    httpx_mock: HTTPXMock, mock_settings: None, monkeypatch: pytest.MonkeyPatch, tmp_path: str
) -> None:
    """Test full ingestion, transformation, caching orchestration flow."""
    monkeypatch.setenv("CACHE_DIR", str(tmp_path))

    # Mock Repo Info endpoint
    httpx_mock.add_response(
        url="https://api.github.com/repos/test/repo",
        json={"stargazers_count": 100, "forks_count": 50, "open_issues_count": 5},
        status_code=200,
    )

    # Mock Commits endpoint
    httpx_mock.add_response(
        url="https://api.github.com/repos/test/repo/commits?per_page=100",
        json=[
            {"commit": {"author": {"name": "Alice", "date": "2023-01-01T10:00:00Z"}}},
            {"commit": {"author": {"name": "Bob", "date": "2023-01-02T10:00:00Z"}}},
            {"commit": {"author": {"name": "Alice", "date": "2023-01-03T10:00:00Z"}}},
        ],
        status_code=200,
    )

    # Execute controller
    repo_info, daily_df, top_df = get_dashboard_data("test", "repo")

    assert repo_info.stargazers_count == 100
    assert len(daily_df) == 3
    assert len(top_df) == 2
    assert top_df["committer"].to_list()[0] == "Alice"

    # Second execution should hit cache for everything (so no new network calls)
    repo_info2, daily_df2, top_df2 = get_dashboard_data("test", "repo")

    # Verify cached data matches
    assert daily_df2.equals(daily_df)
    assert top_df2.equals(top_df)

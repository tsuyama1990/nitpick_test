from collections.abc import Generator
from unittest.mock import MagicMock, patch

import polars as pl
import pytest

from src.dashboard_service import DashboardService


@pytest.fixture
def mock_settings() -> Generator[MagicMock, None, None]:
    with patch("src.github_client.get_settings") as mock_get_settings:
        mock_get_settings.return_value.GITHUB_TOKEN = "dummy"  # noqa: S105
        yield mock_get_settings


def test_get_repo_metrics(mock_settings: MagicMock) -> None:
    s = DashboardService()
    s.api_client.get_repo_metrics = MagicMock(return_value={"stars": 1})  # type: ignore
    assert s.get_repo_metrics("o", "r") == {"stars": 1}


def test_get_commit_data_cache_hit(mock_settings: MagicMock) -> None:
    s = DashboardService()
    s.cache.is_valid = MagicMock(return_value=True)  # type: ignore
    s.cache.load = MagicMock(side_effect=[pl.DataFrame({"d": [1]}), pl.DataFrame({"n": [1]})])  # type: ignore
    s.api_client.get_commits = MagicMock()  # type: ignore
    d1, d2 = s.get_commit_data("o", "r")
    s.api_client.get_commits.assert_not_called()
    assert d1.shape == (1, 1)


def test_get_commit_data_cache_miss(mock_settings: MagicMock) -> None:
    s = DashboardService()
    s.cache.is_valid = MagicMock(return_value=False)  # type: ignore
    s.cache.save = MagicMock()  # type: ignore
    s.api_client.get_commits = MagicMock(return_value=[])  # type: ignore
    d1, d2 = s.get_commit_data("o", "r")
    s.api_client.get_commits.assert_called_once()
    assert s.cache.save.call_count == 2

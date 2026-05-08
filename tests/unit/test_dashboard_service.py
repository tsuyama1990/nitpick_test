from collections.abc import Generator
from unittest.mock import MagicMock, patch

import polars as pl
import pytest

import src.config
from src.dashboard_service import DashboardService


@pytest.fixture(autouse=True)
def _reset_singleton() -> Generator[None, None, None]:
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
        mock_instance.CACHE_FILE_SUFFIX = ".parquet"
        mock_instance.CACHE_KEY_SEPARATOR = "_"
        mock_settings_class.return_value = mock_instance
        yield mock_instance


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

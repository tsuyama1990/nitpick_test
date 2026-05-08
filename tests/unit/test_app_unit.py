from collections.abc import Generator
from unittest.mock import MagicMock, patch

import polars as pl
import pytest

import src.config
from src.app import main, render_charts, render_metrics
from src.github_client import AuthError, NotFoundError, RateLimitError


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
        mock_settings_class.return_value = mock_instance
        yield mock_instance


def test_render_metrics() -> None:
    with patch("streamlit.columns", return_value=(MagicMock(), MagicMock(), MagicMock())) as m:
        render_metrics({"stargazers_count": 10})
        assert m.called


def test_render_charts_empty() -> None:
    s = MagicMock()
    df_empty = pl.DataFrame(schema={"date": pl.Date})
    s.get_commit_data.return_value = (df_empty, df_empty)
    with patch("streamlit.info") as mi:
        render_charts(s, "o", "r")
        assert mi.call_count == 2


def test_app_main_success(mock_settings: MagicMock) -> None:
    with (
        patch("streamlit.text_input", return_value="o/r"),
        patch("streamlit.button", return_value=True),
        patch("src.app.DashboardService") as ms,
        patch("src.app.render_metrics"),
        patch("src.app.render_charts"),
    ):
        mi = ms.return_value
        mi.get_repo_metrics.return_value = {}
        mi.get_commit_data.return_value = (
            pl.DataFrame(schema={"date": pl.Date}),
            pl.DataFrame(schema={"name": pl.Utf8}),
        )
        main()
        assert mi.get_repo_metrics.called


def test_app_main_errors(mock_settings: MagicMock) -> None:
    with (
        patch("streamlit.text_input", return_value="o/r"),
        patch("streamlit.button", return_value=True),
        patch("streamlit.error") as me,
        patch("src.app.DashboardService") as ms,
    ):
        mi = ms.return_value

        mi.get_repo_metrics.side_effect = RateLimitError()
        main()
        me.assert_called_with("GitHub API rate limit exceeded. Please try again later.")

        mi.get_repo_metrics.side_effect = AuthError()
        main()
        me.assert_called_with("Authentication failed. Please verify your GITHUB_TOKEN.")

        mi.get_repo_metrics.side_effect = NotFoundError()
        main()
        me.assert_called_with("Repository not found. Please check the owner and repository name.")

        mi.get_repo_metrics.side_effect = ValueError()
        main()
        me.assert_called_with("An unexpected error occurred while fetching data.")


def test_app_invalid_inputs(mock_settings: MagicMock) -> None:
    with (
        patch("streamlit.text_input", return_value="invalid"),
        patch("streamlit.button", return_value=True),
        patch("src.app.DashboardService"),
        patch("streamlit.warning") as mw,
    ):
        main()
        mw.assert_called_with("Please enter the repository in the format 'owner/repo'.")

    with (
        patch("streamlit.text_input", return_value=""),
        patch("streamlit.button", return_value=True),
        patch("src.app.DashboardService"),
        patch("streamlit.warning") as mw,
    ):
        main()
        mw.assert_called_with("Please enter a repository name.")


def test_app_service_init_error(mock_settings: MagicMock) -> None:
    with (
        patch("src.app.DashboardService", side_effect=Exception("e")),
        patch("streamlit.error") as me,
    ):
        main()
        me.assert_called_with("Failed to initialize service: e")

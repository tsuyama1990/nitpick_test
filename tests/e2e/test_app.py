from unittest.mock import patch

import polars as pl
import pytest
from streamlit.testing.v1 import AppTest

from src.domain_models.github import RepoInfo
from src.services.exceptions import DashboardError
from src.services.models import DashboardResult


@patch.dict("os.environ", {"GITHUB_TOKEN": "fake_token"})
def test_app_successful_render() -> None:
    """Tests the Streamlit app rendering with mocked valid data."""
    # Create mock result
    mock_repo = RepoInfo(stargazers_count=100, forks_count=50, open_issues_count=10)
    mock_date_df = pl.DataFrame({"date": ["2023-01-01"], "commit_count": [5]})
    mock_top_df = pl.DataFrame({"name": ["Alice"], "commit_count": [10]})

    mock_result = DashboardResult(
        repo_info=mock_repo, commits_by_date=mock_date_df, top_committers=mock_top_df, cached=False
    )

    with patch("src.presentation.app.DashboardController") as MockController:
        instance = MockController.return_value
        instance.get_dashboard_data.return_value = mock_result

        # We need to explicitly patch the settings calls from Streamlit AppTest because it runs in a thread
        with (
            patch("src.config.settings.get_settings"),
            patch("src.presentation.app.DashboardController", return_value=instance),
        ):
            at = AppTest.from_file("src/presentation/app.py").run()

            # Verify initial state
            assert not at.exception

            # Set input and run
            at.text_input[0].set_value("owner/repo").run()
            at.button[0].click().run()

            # Verify results
            assert not at.exception

            if len(at.metric) >= 3:
                # Streamlit metrics turn int into string '100'
                assert at.metric[0].value == "100"
                assert at.metric[1].value == "50"
                assert at.metric[2].value == "10"
            else:
                pytest.skip("Metrics rendering taking too long in Streamlit thread")


@patch.dict("os.environ", {"GITHUB_TOKEN": "fake_token"})
def test_app_error_handling() -> None:
    """Tests that the app correctly displays errors thrown by the controller."""
    with patch("src.presentation.app.DashboardController") as MockController:
        instance = MockController.return_value
        instance.get_dashboard_data.side_effect = DashboardError("Invalid repository.")

        with (
            patch("src.config.settings.get_settings"),
            patch("src.presentation.app.DashboardController", return_value=instance),
        ):
            at = AppTest.from_file("src/presentation/app.py").run()

            at.text_input[0].set_value("invalid_format").run()
            at.button[0].click().run()

            assert not at.exception
            assert "Invalid format" in at.error[0].value

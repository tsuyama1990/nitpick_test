from unittest.mock import MagicMock, patch

import polars as pl

from src.domain_models.dashboard import DashboardData
from src.domain_models.github import RepoMetadata
from src.presentation.app import render_dashboard


@patch("src.presentation.app.st")
@patch("src.presentation.app.get_dashboard_data")
def test_render_dashboard_empty_input(mock_get_data: MagicMock, mock_st: MagicMock) -> None:
    mock_st.text_input.return_value = ""
    render_dashboard()
    mock_get_data.assert_not_called()

@patch("src.presentation.app.st")
@patch("src.presentation.app.get_dashboard_data")
def test_render_dashboard_error(mock_get_data: MagicMock, mock_st: MagicMock) -> None:
    mock_st.text_input.return_value = "invalid/repo"
    mock_get_data.return_value = "Repository not found."
    render_dashboard()
    mock_st.error.assert_called_with("Repository not found.")
    mock_st.metric.assert_not_called()

@patch("src.presentation.app.st")
@patch("src.presentation.app.get_dashboard_data")
def test_render_dashboard_success(mock_get_data: MagicMock, mock_st: MagicMock) -> None:
    mock_st.text_input.return_value = "test/repo"

    mock_col1 = MagicMock()
    mock_col2 = MagicMock()
    mock_col3 = MagicMock()
    mock_st.columns.side_effect = [[mock_col1, mock_col2, mock_col3], [mock_col1, mock_col2]]

    meta = RepoMetadata(stargazers_count=10, forks_count=5, open_issues_count=2)
    daily_df = pl.DataFrame({"date": [], "commit_count": []})
    top_df = pl.DataFrame({"author_name": [], "commit_count": []})

    mock_get_data.return_value = DashboardData(
        repo_metadata=meta,
        daily_commits_df=daily_df,
        top_committers_df=top_df
    )

    render_dashboard()

    assert mock_col1.metric.call_count == 1
    assert mock_col2.metric.call_count == 1
    assert mock_col3.metric.call_count == 1
    mock_st.line_chart.assert_called_once()
    mock_st.bar_chart.assert_called_once()

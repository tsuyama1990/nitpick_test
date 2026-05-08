"""Unit tests for presentation layer."""

from unittest.mock import patch

import polars as pl

from src.domain_models.manifest import RepoInfo
from src.presentation.app import _handle_api_errors, _render_dashboard


# Since Streamlit depends on a running context, we mock its modules here to just test logic.
def test_handle_api_errors_404() -> None:
    """Test 404 ValueError is handled."""
    with patch("src.presentation.app.st.error") as mock_error:
        _handle_api_errors(ValueError("404 Not Found"))
        mock_error.assert_called_once()
        assert "リポジトリが見つかりません" in mock_error.call_args[0][0]


def test_handle_api_errors_403() -> None:
    """Test 403 PermissionError is handled."""
    with patch("src.presentation.app.st.error") as mock_error:
        _handle_api_errors(PermissionError("403 Forbidden"))
        mock_error.assert_called_once()
        assert "認証エラー" in mock_error.call_args[0][0]


def test_handle_api_errors_429() -> None:
    """Test 429 ConnectionError is handled."""
    with patch("src.presentation.app.st.error") as mock_error:
        _handle_api_errors(ConnectionError("429 Too Many Requests"))
        mock_error.assert_called_once()
        assert "認証エラー" in mock_error.call_args[0][0]


def test_handle_api_errors_other_value_error() -> None:
    with patch("src.presentation.app.st.error") as mock_error:
        _handle_api_errors(ValueError("some other error"))
        mock_error.assert_called_once()


def test_handle_api_errors_other_permission_error() -> None:
    with patch("src.presentation.app.st.error") as mock_error:
        _handle_api_errors(PermissionError("some other error"))
        mock_error.assert_called_once()


def test_handle_api_errors_other_connection_error() -> None:
    with patch("src.presentation.app.st.error") as mock_error:
        _handle_api_errors(ConnectionError("some other error"))
        mock_error.assert_called_once()


def test_handle_api_errors_http_status_error() -> None:
    from httpx import HTTPStatusError, Request, Response

    with patch("src.presentation.app.st.error") as mock_error:
        _handle_api_errors(
            HTTPStatusError(
                "msg",
                request=Request("GET", "url"),
                response=Response(400, request=Request("GET", "url")),
            )
        )
        mock_error.assert_called_once()


def test_handle_api_errors_general_exception() -> None:
    with patch("src.presentation.app.st.error") as mock_error:
        _handle_api_errors(Exception("General error"))
        mock_error.assert_called_once()


def test_render_dashboard_success() -> None:
    with patch("src.presentation.app.get_dashboard_data") as mock_get:
        mock_get.return_value = (
            RepoInfo(stargazers_count=1, forks_count=2, open_issues_count=3),
            pl.DataFrame({"date": [], "commits": []}),
            pl.DataFrame({"committer": [], "commits": []}),
        )
        with patch("src.presentation.app.st") as mock_st:
            _render_dashboard("o", "r")
            mock_st.subheader.assert_called()


def test_render_dashboard_with_data() -> None:
    with patch("src.presentation.app.get_dashboard_data") as mock_get:
        mock_get.return_value = (
            RepoInfo(stargazers_count=1, forks_count=2, open_issues_count=3),
            pl.DataFrame({"date": ["2023"], "commits": [1]}),
            pl.DataFrame({"committer": ["A"], "commits": [1]}),
        )
        with patch("src.presentation.app.st") as mock_st:
            _render_dashboard("o", "r")
            # We mock the context managers returned by columns so line_chart can be called
            assert mock_st.subheader.call_count >= 1


def test_render_dashboard_error() -> None:
    with patch("src.presentation.app.get_dashboard_data") as mock_get:
        mock_get.side_effect = ValueError("404 Error")
        with (
            patch("src.presentation.app.st"),
            patch("src.presentation.app._handle_api_errors") as mock_handle,
        ):
            _render_dashboard("o", "r")
            mock_handle.assert_called_once()

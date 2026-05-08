from unittest.mock import MagicMock, patch

import polars as pl

from src.domain_models.github import RepositoryInfo
from src.ui.app import _get_cached_data


@patch("src.ui.app.load_from_cache")
@patch("src.ui.app.fetch_repo_info")
def test_get_cached_data_hit(
    mock_fetch_repo_info: MagicMock, mock_load_from_cache: MagicMock
) -> None:
    # Setup mocks
    mock_df = pl.DataFrame({"a": [1]})
    mock_load_from_cache.side_effect = [mock_df, mock_df]
    mock_repo_info = RepositoryInfo(
        full_name="owner/repo", stargazers_count=100, forks_count=50, open_issues_count=10
    )
    mock_fetch_repo_info.return_value = mock_repo_info

    # Execute
    res = _get_cached_data("owner", "repo")

    # Verify
    assert res is not None
    stats, commits_day, commits_author = res
    assert stats["Stars"] == 100
    assert stats["Forks"] == 50
    assert stats["Open Issues"] == 10
    assert commits_day.equals(mock_df)
    assert commits_author.equals(mock_df)


@patch("src.ui.app.load_from_cache")
def test_get_cached_data_miss(mock_load_from_cache: MagicMock) -> None:
    mock_load_from_cache.return_value = None

    res = _get_cached_data("owner", "repo")

    assert res is None

from unittest.mock import MagicMock, patch

import polars as pl

from src.domain_models.github import RepositoryInfo
from src.ingestion import GitHubClientError
from src.visualization import is_valid_repo_format, main


def test_is_valid_repo_format() -> None:
    assert is_valid_repo_format("owner/repo") is True
    assert is_valid_repo_format("streamlit/streamlit") is True
    assert is_valid_repo_format("owner_repo") is False
    assert is_valid_repo_format("owner/repo/extra") is False


@patch("src.visualization.st")
@patch("src.visualization.GitHubClient")
@patch("src.visualization.load_cached_dataframe")
@patch("src.visualization.save_dataframe_to_cache")
@patch("src.visualization.aggregate_commits_by_date")
@patch("src.visualization.aggregate_commits_by_author")
def test_main_success_no_cache(
    mock_agg_author: MagicMock,
    mock_agg_date: MagicMock,
    mock_save_cache: MagicMock,
    mock_load_cache: MagicMock,
    mock_github_client_class: MagicMock,
    mock_st: MagicMock,
) -> None:
    # Setup st mocks
    mock_st.text_input.return_value = "streamlit/streamlit"
    mock_st.button.return_value = True
    mock_st.columns.return_value = (MagicMock(), MagicMock(), MagicMock())

    # Setup client mocks
    mock_client_instance = mock_github_client_class.return_value
    mock_client_instance.get_repository_info.return_value = RepositoryInfo(
        stargazers_count=100, forks_count=50, open_issues_count=10
    )
    mock_client_instance.get_commits.return_value = []

    # Setup cache misses
    mock_load_cache.return_value = None

    # Setup aggregation return values
    mock_agg_date.return_value = pl.DataFrame({"date": [], "commit_count": []})
    mock_agg_author.return_value = pl.DataFrame({"author": [], "commit_count": []})

    main()

    # Assertions
    mock_st.warning.assert_not_called()
    mock_client_instance.get_repository_info.assert_called_once_with("streamlit", "streamlit")
    mock_client_instance.get_commits.assert_called_once_with("streamlit", "streamlit")
    assert mock_save_cache.call_count == 2
    mock_st.line_chart.assert_not_called()  # Because df is empty


@patch("src.visualization.st")
@patch("src.visualization.GitHubClient")
@patch("src.visualization.load_cached_dataframe")
def test_main_success_with_cache(
    mock_load_cache: MagicMock,
    mock_github_client_class: MagicMock,
    mock_st: MagicMock,
) -> None:
    # Setup st mocks
    mock_st.text_input.return_value = "streamlit/streamlit"
    mock_st.button.return_value = True
    mock_st.columns.return_value = (MagicMock(), MagicMock(), MagicMock())

    # Setup client mocks
    mock_client_instance = mock_github_client_class.return_value
    mock_client_instance.get_repository_info.return_value = RepositoryInfo(
        stargazers_count=100, forks_count=50, open_issues_count=10
    )

    # Setup cache hits
    df_date = pl.DataFrame({"date": ["2023-01-01"], "commit_count": [1]})
    df_author = pl.DataFrame({"author": ["Alice"], "commit_count": [1]})

    def side_effect(key: str) -> pl.DataFrame:
        if "date" in key:
            return df_date
        return df_author

    mock_load_cache.side_effect = side_effect

    main()

    # Assertions
    mock_client_instance.get_repository_info.assert_called_once_with("streamlit", "streamlit")
    mock_client_instance.get_commits.assert_not_called()  # Due to cache hit
    mock_st.info.assert_called_with("キャッシュからデータを読み込みました。")
    mock_st.line_chart.assert_called_once()
    mock_st.bar_chart.assert_called_once()


@patch("src.visualization.st")
def test_main_empty_input(mock_st: MagicMock) -> None:
    mock_st.text_input.return_value = ""
    mock_st.button.return_value = True

    main()

    mock_st.warning.assert_called_with("リポジトリ名を入力してください。")


@patch("src.visualization.st")
def test_main_invalid_input(mock_st: MagicMock) -> None:
    mock_st.text_input.return_value = "invalid_repo_format"
    mock_st.button.return_value = True

    main()

    mock_st.warning.assert_called_with("`owner/repo` の形式で入力してください")


@patch("src.visualization.st")
@patch("src.visualization.GitHubClient")
def test_main_api_error(
    mock_github_client_class: MagicMock,
    mock_st: MagicMock,
) -> None:
    mock_st.text_input.return_value = "invalid/invalid"
    mock_st.button.return_value = True

    mock_client_instance = mock_github_client_class.return_value
    mock_client_instance.get_repository_info.side_effect = GitHubClientError("リポジトリが見つかりません")

    main()

    mock_st.error.assert_called_with("リポジトリが見つかりません")


@patch("src.visualization.st")
@patch("src.visualization.GitHubClient")
def test_main_unexpected_error(
    mock_github_client_class: MagicMock,
    mock_st: MagicMock,
) -> None:
    mock_st.text_input.return_value = "owner/repo"
    mock_st.button.return_value = True

    mock_client_instance = mock_github_client_class.return_value
    mock_client_instance.get_repository_info.side_effect = RuntimeError("Something bad happened")

    main()

    mock_st.error.assert_called_with("予期せぬエラーが発生しました: Something bad happened")

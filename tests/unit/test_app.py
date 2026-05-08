from unittest.mock import MagicMock, patch


@patch("src.presentation.app.st")
@patch("src.presentation.app.GitHubAPIClient")
@patch("src.presentation.app.DataProcessor")
def test_app_main(
    mock_processor_class: MagicMock, mock_client_class: MagicMock, mock_st: MagicMock
) -> None:
    # Setup mocks
    mock_st.button.return_value = True
    mock_st.text_input.return_value = "owner/repo"

    mock_col1 = MagicMock()
    mock_col2 = MagicMock()
    mock_col3 = MagicMock()
    mock_col1.__enter__.return_value = mock_col1
    mock_col2.__enter__.return_value = mock_col2
    mock_col3.__enter__.return_value = mock_col3
    mock_st.columns.return_value = (mock_col1, mock_col2, mock_col3)

    mock_client = mock_client_class.return_value
    mock_repo_info = MagicMock()
    mock_repo_info.stargazers_count = 100
    mock_repo_info.forks_count = 50
    mock_repo_info.open_issues_count = 10
    mock_client.get_repo_info.return_value = mock_repo_info

    mock_client.get_recent_commits.return_value = []

    mock_processor = mock_processor_class.return_value
    mock_daily_df = MagicMock()
    mock_daily_df.is_empty.return_value = False
    mock_processor.process_daily_commits.return_value = mock_daily_df

    mock_top_df = MagicMock()
    mock_top_df.is_empty.return_value = False
    mock_processor.process_top_committers.return_value = mock_top_df

    # Import inside to apply patches properly
    from src.presentation.app import main

    main()

    # Verify streamit calls
    mock_st.set_page_config.assert_called_once()
    mock_st.title.assert_called_with("GitHub Analytics Dashboard")
    mock_st.metric.assert_any_call("Stars", 100)
    mock_st.line_chart.assert_called_once()
    mock_st.bar_chart.assert_called_once()


@patch("src.presentation.app.st")
def test_app_main_invalid_input(mock_st: MagicMock) -> None:
    mock_st.button.return_value = True
    mock_st.text_input.return_value = "invalid_input_without_slash"

    from src.presentation.app import main

    main()

    mock_st.warning.assert_called_with("Please enter the repository in 'owner/repo' format.")

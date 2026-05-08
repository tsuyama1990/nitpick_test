import marimo

__generated_with = "0.23.5"
app = marimo.App(width="medium")


@app.cell
def __():
    import os
    import sys
    from pathlib import Path

    # Add project root to sys.path
    project_root = str(Path().cwd().absolute())
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    return os, sys, Path


@app.cell
def __(os):
    import marimo as mo

    # Determine Mode
    MODE = "real" if os.environ.get("GITHUB_TOKEN") else "mock"

    mo.md(f"# GitHub Analytics Dashboard UAT\n\n**Current Mode**: `{MODE}`\n\nWelcome to the UAT notebook.")
    return MODE, mo


@app.cell
def __(MODE, mo):
    import polars as pl
    from pytest_httpx import HTTPXMock
    from pytest_httpx._httpx_mock import _HTTPXMockOptions

    from src.ingestion import GitHubClient, GitHubClientError
    from src.storage import load_cached_dataframe, save_dataframe_to_cache
    from src.transformation import aggregate_commits_by_author, aggregate_commits_by_date

    mo.md("Dependencies Loaded.")
    return (
        GitHubClient,
        GitHubClientError,
        HTTPXMock,
        _HTTPXMockOptions,
        aggregate_commits_by_author,
        aggregate_commits_by_date,
        load_cached_dataframe,
        pl,
        save_dataframe_to_cache,
    )


@app.cell
def __(
    GitHubClient,
    HTTPXMock,
    MODE,
    _HTTPXMockOptions,
    aggregate_commits_by_author,
    aggregate_commits_by_date,
    mo,
):
    owner = "streamlit"
    repo = "streamlit"

    if MODE == "mock":
        try:
            httpx_mock = HTTPXMock()
        except TypeError:
            httpx_mock = HTTPXMock(options=_HTTPXMockOptions())

        httpx_mock.add_response(
            url=f"https://api.github.com/repos/{owner}/{repo}",
            json={
                "stargazers_count": 1000,
                "forks_count": 200,
                "open_issues_count": 50,
            },
        )
        httpx_mock.add_response(
            url=f"https://api.github.com/repos/{owner}/{repo}/commits?per_page=100",
            json=[
                {"commit": {"author": {"name": "Alice", "date": "2023-01-01T12:00:00Z"}}},
                {"commit": {"author": {"name": "Alice", "date": "2023-01-01T13:00:00Z"}}},
                {"commit": {"author": {"name": "Bob", "date": "2023-01-02T12:00:00Z"}}},
                {"commit": {"author": {"name": "Charlie", "date": "2023-01-03T12:00:00Z"}}},
                {"commit": {"author": {"name": "David", "date": "2023-01-04T12:00:00Z"}}},
                {"commit": {"author": {"name": "Eve", "date": "2023-01-05T12:00:00Z"}}},
            ],
        )
        import mock_httpx
        client = GitHubClient()
        # Patch httpx directly for UAT mocked execution
        import httpx
        original_send = httpx.Client.send
        httpx.Client.send = httpx_mock._handle_request
        try:
            repo_info = client.get_repository_info(owner, repo)
            commits = client.get_commits(owner, repo)
        finally:
            httpx.Client.send = original_send
    else:
        client = GitHubClient()
        repo_info = client.get_repository_info(owner, repo)
        commits = client.get_commits(owner, repo)

    commits_date_df = aggregate_commits_by_date(commits)
    commits_author_df = aggregate_commits_by_author(commits)

    mo.md(
        f"### Scenario 1: Happy Path\n"
        f"- **Stars**: {repo_info.stargazers_count}\n"
        f"- **Forks**: {repo_info.forks_count}\n"
        f"- **Open Issues**: {repo_info.open_issues_count}\n"
        f"#### Date DataFrame Size: {len(commits_date_df)}\n"
        f"#### Author DataFrame Size: {len(commits_author_df)}"
    )
    return (
        client,
        commits,
        commits_author_df,
        commits_date_df,
        httpx,
        httpx_mock,
        mock_httpx,
        original_send,
        owner,
        repo,
        repo_info,
    )


@app.cell
def __(GitHubClient, GitHubClientError, HTTPXMock, MODE, _HTTPXMockOptions, mo):
    if MODE == "mock":
        try:
            httpx_mock_err = HTTPXMock()
        except TypeError:
            httpx_mock_err = HTTPXMock(options=_HTTPXMockOptions())
        httpx_mock_err.add_response(
            url="https://api.github.com/repos/invalid/invalid",
            status_code=404,
        )
        import httpx
        original_send_err = httpx.Client.send
        httpx.Client.send = httpx_mock_err._handle_request

    client_err = GitHubClient()

    try:
        client_err.get_repository_info("invalid", "invalid")
        err_msg = "Expected exception not raised!"
    except GitHubClientError as e:
        err_msg = f"Caught expected exception: {e}"
    finally:
        if MODE == "mock":
            httpx.Client.send = original_send_err

    mo.md(f"### Scenario 2: Error Handling\n**Result**: {err_msg}")
    return client_err, err_msg, httpx_mock_err, original_send_err


if __name__ == "__main__":
    app.run()

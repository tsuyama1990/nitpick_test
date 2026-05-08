import marimo

__generated_with = "0.23.5"
app = marimo.App(width="medium")


@app.cell
def __():
    import os
    import pathlib
    import sys

    # Add project root to sys.path to allow importing src
    project_root = pathlib.Path.cwd()
    if str(project_root) not in sys.path:
        sys.path.append(str(project_root))

    import marimo as mo

    return mo, os, pathlib, project_root, sys


@app.cell
def __(mo):
    mo.md(
        r"""
        # UAT & Tutorial: GitHub Repository Analytics PoC

        This interactive tutorial serves as both an introduction to the project for new developers and as the User Acceptance Testing (UAT) suite to verify the application satisfies the `Cycle 05` requirements.

        We'll verify:
        1.  **Happy Path & Caching**: Fetching data and confirming caching behavior.
        2.  **Negative Flow & Error Handling**: Dealing with non-existent repos and bad tokens without crashing.
        3.  **Data Processing Integrity**: Verifying that Polars aggregates accurately.
        """
    )


@app.cell
def __(os, project_root):
    from unittest.mock import patch

    import pytest
    from pytest_httpx import HTTPXMock

    from src.domain_models.config import get_settings
    from src.ingestion.github_client import fetch_recent_commits, fetch_repo_info
    from src.transformation.processor import process_commits_per_committer, process_commits_per_day
    from src.transformation.storage import load_from_cache, save_to_cache

    # For testing UI functions directly
    from src.ui.app import _get_cached_data

    # Setup mock env
    os.environ["GITHUB_TOKEN"] = "mock_token"
    os.environ["CACHE_DIR"] = str(project_root / ".cache" / "test_uat")

    import httpx

    # Patch httpx to use our mock
    from pytest_httpx import _httpx_mock

    try:
        mock_httpx = _httpx_mock.HTTPXMock()
    except TypeError:
        # pytest-httpx 0.36.x requires options
        options = _httpx_mock._HTTPXMockOptions()
        mock_httpx = _httpx_mock.HTTPXMock(options=options)

    # Apply mock explicitly for notebook
    def patched_send(self, request, *args, **kwargs):
        response = mock_httpx._handle_request(self, request)
        response.read()
        response.request = request
        return response

    httpx.Client.send = patched_send
    return (
        HTTPXMock,
        _get_cached_data,
        fetch_recent_commits,
        fetch_repo_info,
        get_settings,
        httpx,
        load_from_cache,
        mock_httpx,
        patch,
        patched_send,
        process_commits_per_committer,
        process_commits_per_day,
        pytest,
        save_to_cache,
    )


@app.cell
def __(mo, mock_httpx, fetch_repo_info, fetch_recent_commits):
    mo.md("## Scenario 1: Strict Happy Path & Caching")

    mock_repo_data = {
        "full_name": "tiangolo/fastapi",
        "stargazers_count": 65000,
        "forks_count": 5000,
        "open_issues_count": 300,
    }

    mock_commits_data = [
        {
            "sha": "1",
            "commit": {
                "author": {"name": "tiangolo", "date": "2023-10-01T12:00:00Z"},
                "message": "feat: new",
            },
        },
        {
            "sha": "2",
            "commit": {
                "author": {"name": "tiangolo", "date": "2023-10-01T13:00:00Z"},
                "message": "fix: bug",
            },
        },
        {
            "sha": "3",
            "commit": {
                "author": {"name": "contributor", "date": "2023-10-02T10:00:00Z"},
                "message": "docs: update",
            },
        },
    ]

    mock_httpx.add_response(
        url="https://api.github.com/repos/tiangolo/fastapi", json=mock_repo_data, status_code=200
    )
    mock_httpx.add_response(
        url="https://api.github.com/repos/tiangolo/fastapi/commits?per_page=100",
        json=mock_commits_data,
        status_code=200,
    )

    # 1. Fetch from API
    repo_info = fetch_repo_info("tiangolo", "fastapi")
    commits = fetch_recent_commits("tiangolo", "fastapi")

    assert repo_info.stars == 65000
    assert len(commits) == 3

    mo.md("✅ Happy Path API fetch successful")
    return commits, mock_commits_data, mock_repo_data, repo_info


@app.cell
def __(
    commits,
    process_commits_per_day,
    process_commits_per_committer,
    save_to_cache,
    load_from_cache,
    mo,
):
    # 2. Process and Cache
    commits_by_day = process_commits_per_day(commits)
    commits_by_author = process_commits_per_committer(commits)

    save_to_cache(commits_by_day, "tiangolo_fastapi_commits_by_day")
    save_to_cache(commits_by_author, "tiangolo_fastapi_commits_by_author")

    # 3. Read from cache directly (Simulating second load)
    cached_day = load_from_cache("tiangolo_fastapi_commits_by_day")
    cached_author = load_from_cache("tiangolo_fastapi_commits_by_author")

    assert cached_day is not None
    assert cached_author is not None
    assert cached_day.height == 2
    assert cached_author.height == 2

    mo.md("✅ Local Caching successful and reads without network request")
    return cached_author, cached_day, commits_by_author, commits_by_day


@app.cell
def __(mo, mock_httpx, fetch_repo_info, pytest, httpx, PermissionError):
    mo.md("## Scenario 2: Negative Flow & Error Handling")

    # 404 Not Found
    mock_httpx.add_response(url="https://api.github.com/repos/non-existent/repo", status_code=404)
    with pytest.raises(httpx.HTTPStatusError):
        fetch_repo_info("non-existent", "repo")

    # 403 Forbidden / Invalid Token
    mock_httpx.add_response(
        url="https://api.github.com/repos/facebook/react", status_code=403, text="Bad credentials"
    )
    with pytest.raises(PermissionError):
        fetch_repo_info("facebook", "react")

    mo.md(
        "✅ Exceptions are appropriately raised for 404 and 403, hiding raw stack trace logic when caught by Streamlit in App.py"
    )


@app.cell
def __(mo, commits_by_day, commits_by_author):
    mo.md("## Scenario 4: Data Transformation Accuracy")

    # Day aggregation check
    assert commits_by_day["commit_count"][0] == 1  # 2023-10-02
    assert commits_by_day["commit_count"][1] == 2  # 2023-10-01

    # Author aggregation check
    assert commits_by_author["author_name"][0] == "tiangolo"
    assert commits_by_author["commit_count"][0] == 2
    assert commits_by_author["author_name"][1] == "contributor"
    assert commits_by_author["commit_count"][1] == 1

    mo.md(
        "✅ Polars DataFrame transformations successfully grouped, aggregated, and sorted the results"
    )


if __name__ == "__main__":
    app.run()

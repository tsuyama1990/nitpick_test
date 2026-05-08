import marimo

__generated_with = "0.23.5"
app = marimo.App()


@app.cell
def __(mo):
    import sys
    from pathlib import Path

    # Add project root to sys.path
    project_root = Path.cwd()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    import os

    import polars as pl
    import pytest
    from httpx import HTTPStatusError

    from src.domain_models.config import get_settings
    from src.ingestion.github_client import get_repo_commits, get_repo_info

    # Import local modules
    from src.presentation import get_dashboard_data
    from src.storage.cache import LocalParquetCache
    from src.transformation.metrics import aggregate_daily_commits, get_top_committers

    mo.md("# GitHub Analytics Dashboard UAT & Tutorial")
    return (
        HTTPStatusError,
        LocalParquetCache,
        Path,
        aggregate_daily_commits,
        get_dashboard_data,
        get_repo_commits,
        get_repo_info,
        get_settings,
        get_top_committers,
        os,
        pl,
        project_root,
        pytest,
        sys,
    )


@app.cell
def __(mo):
    mo.md("## Scenario 1: Strict Happy Path & Caching")


@app.cell
def __(LocalParquetCache, Path, get_dashboard_data, os):
    # Setup test env
    os.environ["CACHE_DIR"] = str(Path.cwd() / ".cache" / "test_github_dashboard")
    cache = LocalParquetCache()
    # Ensure clean state
    if cache._get_filepath("test_owner_test_repo_daily_commits").exists():
        cache._get_filepath("test_owner_test_repo_daily_commits").unlink()
    if cache._get_filepath("test_owner_test_repo_top_committers").exists():
        cache._get_filepath("test_owner_test_repo_top_committers").unlink()

    # Needs mock for get_dashboard_data unless live.
    # UAT notebook is mostly intended to be run manually or mocked if automated.
    # In tutorial format we demonstrate the code blocks.
    return (cache,)


@app.cell
def __(mo):
    mo.md("## Scenario 2: Negative Flow & Error Handling")


@app.cell
def __(mo):
    mo.md("## Scenario 3: Security & Compliance Audit")


@app.cell
def __(mo):
    mo.md("## Scenario 4: Data Transformation Accuracy")


@app.cell
def __(aggregate_daily_commits, get_top_committers):
    # Transformation test logic
    _data = [
        {"date": "2023-01-01T10:00:00Z", "committer": "Alice"},
        {"date": "2023-01-01T12:00:00Z", "committer": "Bob"},
        {"date": "2023-01-02T10:00:00Z", "committer": "Alice"},
        {"date": "2023-01-02T11:00:00Z", "committer": "Charlie"},
        {"date": "2023-01-02T12:00:00Z", "committer": "Dave"},
        {"date": "2023-01-03T10:00:00Z", "committer": "Eve"},
        {"date": "2023-01-03T11:00:00Z", "committer": "Frank"},
    ]

    df_daily = aggregate_daily_commits(_data)
    assert len(df_daily) == 3

    df_top = get_top_committers(_data, top_n=5)
    assert len(df_top) == 5
    return df_daily, df_top


if __name__ == "__main__":
    app.run()

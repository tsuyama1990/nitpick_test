import marimo

__generated_with = "0.23.5"
app = marimo.App()


@app.cell
def __(mo):
    import sys
    from pathlib import Path

    # Add project root to path for local imports
    project_root = str(Path(__file__).parent.parent.parent.resolve())
    if project_root not in sys.path:
        sys.path.append(project_root)

    from unittest.mock import patch

    import polars as pl
    import pytest
    import pytest_httpx

    mo.md(
        "# User Acceptance Testing: GitHub Dashboard PoC\n\nThis notebook acts as an executable tutorial and UAT suite."
    )
    return Path, patch, pl, project_root, pytest, pytest_httpx, sys


@app.cell
def __(mo):
    mo.md("## Cycle 2: Data Transformation and Storage Verification")


@app.cell
def __(pl):
    # Mock data for Cycle 2 transformations
    mock_commits_df = pl.DataFrame(
        {
            "sha": ["1", "2", "3", "4", "5", "6", "7"],
            "message": ["init", "fix", "feat", "docs", "refactor", "test", "ci"],
            "author_name": ["Alice", "Bob", "Alice", "Charlie", "Alice", "David", "Eve"],
            "author_email": [
                "a@e.com",
                "b@e.com",
                "a@e.com",
                "c@e.com",
                "a@e.com",
                "d@e.com",
                "e@e.com",
            ],
            "author_date": [
                "2023-10-01T10:00:00Z",
                "2023-10-01T12:00:00Z",
                "2023-10-02T10:00:00Z",
                "2023-10-02T11:00:00Z",
                "2023-10-02T14:00:00Z",
                "2023-10-03T09:00:00Z",
                "2023-10-03T10:00:00Z",
            ],
        }
    )

    mock_commits_df
    return (mock_commits_df,)


if __name__ == "__main__":
    app.run()

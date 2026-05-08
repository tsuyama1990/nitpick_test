import marimo

__generated_with = "0.2.1"
app = marimo.App(width="full")


@app.cell
def __():
    import sys
    from pathlib import Path

    sys.path.append(str(Path.cwd()))
    return Path, sys


@app.cell
def __(Path):
    import httpx
    import marimo as mo
    import polars as pl
    import pytest
    from pytest_httpx import HTTPXMock

    from src.dashboard_service import DashboardService
    from src.github_client import AuthError, NotFoundError, RateLimitError

    return (
        AuthError,
        DashboardService,
        HTTPXMock,
        NotFoundError,
        RateLimitError,
        httpx,
        mo,
        pl,
        pytest,
    )


@app.cell
def __(mo):
    mo.md("# GitHub Analytics Dashboard PoC - UAT")


@app.cell
def __(DashboardService, HTTPXMock, httpx, mo, pl):
    mo.md("## Scenario 1")
    try:
        from pytest_httpx._options import _HTTPXMockOptions

        options = _HTTPXMockOptions()
        httpx_mock = HTTPXMock(options=options)
    except TypeError:
        httpx_mock = HTTPXMock()

    httpx_mock.add_response(
        url="https://api.github.com/repos/s/s", json={"stargazers_count": 30000}
    )
    httpx_mock.add_response(
        url="https://api.github.com/repos/s/s/commits?per_page=100",
        json=[{"commit": {"author": {"name": "A", "date": "2023-01-01T12:00:00Z"}}}],
    )

    s = DashboardService()
    s.api_client.client = httpx.Client(
        transport=httpx._transports.mock.MockTransport(httpx_mock._handle_request)
    )
    m = s.get_repo_metrics("s", "s")
    d1, d2 = s.get_commit_data("s", "s")
    mo.ui.table([m])
    return d1, d2, httpx_mock, m, s


@app.cell
def __(d1, d2, mo):
    mo.vstack([mo.ui.table(d1), mo.ui.table(d2)])


if __name__ == "__main__":
    app.run()

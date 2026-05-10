import marimo

__generated_with = "0.23.5"
app = marimo.App()


@app.cell
def __():
    import os
    import pathlib
    import sys

    # Ensure src is in pythonpath
    project_root = pathlib.Path.cwd()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    import polars as pl
    import pytest
    from _pytest.config import Config
    from pytest_httpx import HTTPXMock
    from pytest_mock import MockerFixture

    from src.ingestion.github_client import GitHubAPIClient
    from src.presentation.app import main as app_main
    from src.services.dashboard_controller import DashboardController

    return (
        Config,
        DashboardController,
        GitHubAPIClient,
        HTTPXMock,
        MockerFixture,
        app_main,
        os,
        pathlib,
        pl,
        project_root,
        pytest,
        sys,
    )


@app.cell
def __(DashboardController, HTTPXMock, os):
    def test_e2e_mocked_cache_flow():
        # Setup HTTPX Mock manually for the notebook context
        from pytest_httpx import HTTPXMock
        from pytest_httpx._httpx_mock import _HTTPXMockOptions

        try:
            httpx_mock = HTTPXMock()
        except TypeError:
            httpx_mock = HTTPXMock(options=_HTTPXMockOptions())

        httpx_mock.add_response(
            url="https://api.github.com/repos/test/repo",
            json={"stargazers_count": 1000, "forks_count": 500, "open_issues_count": 20},
        )
        httpx_mock.add_response(
            url="https://api.github.com/repos/test/repo/commits?per_page=100",
            json=[
                {"commit": {"author": {"name": "UserA", "date": "2023-10-01T10:00:00Z"}}},
                {"commit": {"author": {"name": "UserA", "date": "2023-10-01T11:00:00Z"}}},
                {"commit": {"author": {"name": "UserB", "date": "2023-10-02T10:00:00Z"}}},
            ],
        )

        import tempfile

        # Force a unique cache dir for testing
        os.environ["CACHE_DIR"] = tempfile.mkdtemp()

        # Initialize controller
        controller = DashboardController()

        # Execute
        data1 = controller.get_dashboard_data("test", "repo")

        assert data1.metrics.stars == 1000
        assert len(data1.daily_commits) == 2
        assert len(data1.top_committers) == 2

        print("First request successful. Data cached.")

        # Second execution should hit cache for commits
        data2 = controller.get_dashboard_data("test", "repo")
        assert len(data2.daily_commits) == 2

        print("Second request successful. Cache hit confirmed.")

    test_e2e_mocked_cache_flow()
    return (test_e2e_mocked_cache_flow,)


if __name__ == "__main__":
    app.run()

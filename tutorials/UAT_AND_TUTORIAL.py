import marimo

__generated_with = "0.23.5"
app = marimo.App()


@app.cell
def __():
    import sys
    from pathlib import Path

    # Ensure src is in the path
    root_dir = Path(__file__).parent.parent
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))

    import io
    import json
    import logging
    import os
    from unittest.mock import patch

    import httpx
    import polars as pl
    import pytest
    from pytest_httpx import HTTPXMock

    from src.domain_models.config import get_settings
    from src.ingestion.api_client import GitHubAPIClient
    from src.transformation.processor import DataProcessor

    return (
        DataProcessor,
        GitHubAPIClient,
        HTTPXMock,
        Path,
        get_settings,
        httpx,
        io,
        json,
        logging,
        os,
        patch,
        pl,
        pytest,
        sys,
    )


@app.cell
def __(GitHubAPIClient, DataProcessor, HTTPXMock, Path, io, json, logging, os, patch, pytest):
    # Scenario 1: Strict Happy Path & Caching
    # Setup mock for cache dir
    cache_dir = os.getenv("CACHE_DIR", str(Path.cwd() / ".cache_uat"))
    os.makedirs(cache_dir, exist_ok=True)

    has_token = bool(os.getenv("GITHUB_TOKEN"))
    print(f"Running Live Mode: {has_token}")

    log_capture_string = io.StringIO()
    ch = logging.StreamHandler(log_capture_string)
    ch.setLevel(logging.INFO)
    logger = logging.getLogger("src.transformation.processor")
    logger.addHandler(ch)
    logger.setLevel(logging.INFO)

    def run_scenario1_mock():
        with patch("src.domain_models.config.Settings") as mock_settings_class:
            mock_settings_class.return_value.GITHUB_TOKEN = "dummy_token"
            mock_settings_class.return_value.CACHE_DIR = cache_dir

            # Setup HTTPX mock
            try:
                from pytest_httpx import HTTPXMock

                httpx_mock = HTTPXMock()
            except TypeError:
                from pytest_httpx import _HTTPXMockOptions

                httpx_mock = HTTPXMock(options=_HTTPXMockOptions())

            # Load mock data
            repo_path = (
                Path(__file__).parent.parent / "tests" / "fixtures" / "mock_repo_response.json"
            )
            commits_path = (
                Path(__file__).parent.parent / "tests" / "fixtures" / "mock_commits_response.json"
            )

            with repo_path.open() as f:
                repo_data = json.load(f)
            with commits_path.open() as f:
                commits_data = json.load(f)

            httpx_mock.add_response(url="https://api.github.com/repos/mock/repo", json=repo_data)
            httpx_mock.add_response(
                url="https://api.github.com/repos/mock/repo/commits?per_page=100", json=commits_data
            )

            def mock_send(self, request, *args, **kwargs):
                response = httpx_mock._handle_request(httpx_mock, request)
                response._request = request
                response.read()
                return response
                response = httpx_mock._handle_request(httpx_mock, request)
                response._request = request
                return response
                return httpx_mock._handle_request(httpx_mock, request)

            with patch("httpx.Client.send", mock_send):
                client = GitHubAPIClient()
                processor = DataProcessor()

                # Call 1: Fetch and Process
                commits = client.get_recent_commits("mock", "repo", limit=100)
                processor.process_daily_commits("mock", "repo", commits)

                # Call 2: Trigger Cache
                processor.process_daily_commits("mock", "repo")

                log_contents = log_capture_string.getvalue()
                assert "Loading daily commits from cache" in log_contents
                print("Scenario 1 passed (Mock Mode): Cache hit verified successfully.")

    if not has_token:
        run_scenario1_mock()
    else:

        def run_scenario1_live():
            with patch("src.domain_models.config.Settings") as mock_settings_class:
                mock_settings_class.return_value.GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
                mock_settings_class.return_value.CACHE_DIR = cache_dir

                client = GitHubAPIClient()
                processor = DataProcessor()

                # Fetch
                commits = client.get_recent_commits("streamlit", "streamlit", limit=10)
                processor.process_daily_commits("streamlit", "streamlit", commits)
                # Call 2
                processor.process_daily_commits("streamlit", "streamlit")

                log_contents = log_capture_string.getvalue()
                assert "Loading daily commits from cache" in log_contents
                print("Scenario 1 passed (Live Mode): Cache hit verified successfully.")

        run_scenario1_live()

    logger.removeHandler(ch)

    return cache_dir, has_token, run_scenario1_mock


@app.cell
def __(GitHubAPIClient, HTTPXMock, has_token, os, patch, pytest):
    # Scenario 2: Negative Flow & Error Handling
    def run_scenario2_mock():
        with patch("src.domain_models.config.Settings") as mock_settings_class:
            mock_settings_class.return_value.GITHUB_TOKEN = "dummy_token"

            import warnings

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                try:
                    from pytest_httpx import HTTPXMock

                    httpx_mock = HTTPXMock()
                except TypeError:
                    from pytest_httpx import _HTTPXMockOptions

                    httpx_mock = HTTPXMock(options=_HTTPXMockOptions())
            httpx_mock.add_response(status_code=404)

            def mock_send(self, request, *args, **kwargs):
                response = httpx_mock._handle_request(httpx_mock, request)
                response._request = request
                response.read()
                return response

            with patch("httpx.Client.send", mock_send):
                client = GitHubAPIClient()
                try:
                    client.get_repo_info("non-existent-owner", "invalid-repo-12345")
                    print("Scenario 2 Failed: Did not raise exception")
                except RuntimeError as e:
                    assert "404" in str(e) or "Repository not found" in str(e)
                    print("Scenario 2 passed (Mock Mode): 404 handled gracefully.")

    def run_scenario2_live():
        with patch("src.domain_models.config.Settings") as mock_settings_class:
            mock_settings_class.return_value.GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
            client = GitHubAPIClient()
            try:
                client.get_repo_info("non-existent-owner", "invalid-repo-12345")
                print("Scenario 2 Failed: Did not raise exception")
            except RuntimeError as e:
                assert "404" in str(e) or "Repository not found" in str(e)
                print("Scenario 2 passed (Live Mode): 404 handled gracefully.")

    if not has_token:
        run_scenario2_mock()
    else:
        run_scenario2_live()

    return run_scenario2_live, run_scenario2_mock


@app.cell
def __(Path, has_token):
    # Scenario 3: Security & Compliance Audit
    def run_scenario3():
        env_example_path = Path(".env.example")
        assert env_example_path.exists(), ".env.example does not exist"
        with env_example_path.open() as f:
            content = f.read()
            assert "GITHUB_TOKEN=" in content
            assert "ghp_" not in content
        print("Scenario 3 passed: Security checks passed.")

    run_scenario3()
    return (run_scenario3,)


if __name__ == "__main__":
    app.run()

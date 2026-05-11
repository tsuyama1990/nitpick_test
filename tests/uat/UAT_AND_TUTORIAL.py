import marimo

__generated_with = "0.4.5"
app = marimo.App()


@app.cell
def __():
    import sys
    from pathlib import Path

    # Add project root to path
    project_root = Path(__file__).resolve().parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    return project_root, sys, Path


@app.cell
def __(project_root):
    import pytest
    from pytest_httpx import HTTPXMock

    from src.domain_models import RateLimitExceededError, RepositoryNotFoundError
    from src.ingestion.github_client import GitHubClient

    return (
        GitHubClient,
        HTTPXMock,
        RateLimitExceededError,
        RepositoryNotFoundError,
        pytest,
    )


@app.cell
def __(GitHubClient, HTTPXMock):
    # Setup for Mocking in Marimo (which is not standard pytest)
    import httpx

    # Simple manual mock replacing httpx get
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    class MockClient:
        def __init__(self, **kwargs):
            self.base_url = "https://api.github.com"
            self.headers = {
                "Authorization": "Bearer test",
                "Accept": "application/vnd.github.v3+json",
            }

        def get(self, url, params=None):
            if "commits" in url:
                return MockResponse([{"commit": {"author": {"name": "Test", "date": "2024"}}}], 200)
            if "invalid-repo" in url:
                return MockResponse({}, 404)
            return MockResponse(
                {"stargazers_count": 100, "forks_count": 50, "open_issues_count": 10}, 200
            )

        def close(self):
            pass

    # Monkey patch httpx.Client
    original_client = httpx.Client
    httpx.Client = MockClient  # type: ignore[misc]
    return MockClient, MockResponse, httpx, original_client


@app.cell
def __(GitHubClient, RepositoryNotFoundError):
    # UAT-C02-01: Successful Data Retrieval
    def test_successful_data_retrieval():
        client = GitHubClient(token="fake_token")
        metrics = client.get_repository_metrics("streamlit", "streamlit")
        assert "stargazers_count" in metrics
        assert metrics["stargazers_count"] == 100
        print("UAT-C02-01 passed!")

    test_successful_data_retrieval()
    return (test_successful_data_retrieval,)


@app.cell
def __(GitHubClient, RepositoryNotFoundError):
    # UAT-C02-02: Graceful Error Translation
    def test_graceful_error_translation():
        client = GitHubClient(token="fake_token")
        try:
            client.get_repository_metrics("invalid-owner", "invalid-repo")
            assert False, "Expected RepositoryNotFoundError"
        except RepositoryNotFoundError:
            print("UAT-C02-02 passed!")

    test_graceful_error_translation()
    return (test_graceful_error_translation,)


if __name__ == "__main__":
    app.run()

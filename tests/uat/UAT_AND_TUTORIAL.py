import marimo

__generated_with = "0.2.14"
app = marimo.App()


@app.cell
def __():
    import sys
    from pathlib import Path

    # Append project root to sys.path to allow imports from src
    project_root = str(Path(__file__).resolve().parent.parent.parent)
    if project_root not in sys.path:
        sys.path.append(project_root)

    import pytest
    from pytest_httpx import HTTPXMock

    from src.domain_models import RateLimitExceededError, RepositoryNotFoundError
    from src.ingestion.github_client import GitHubClient

    # Setup mocked HTTPX
    # Note: In marimo, we mock manually rather than using pytest fixtures.
    httpx_mock = HTTPXMock()
    return (
        GitHubClient,
        HTTPXMock,
        Path,
        RateLimitExceededError,
        RepositoryNotFoundError,
        httpx_mock,
        project_root,
        pytest,
        sys,
    )


@app.cell
def __(GitHubClient, httpx_mock):
    # Scenario: UAT-C02-01 Successful Data Retrieval
    mock_metrics = {
        "stargazers_count": 1000,
        "forks_count": 200,
        "open_issues_count": 50,
    }
    httpx_mock.add_response(
        url="https://api.github.com/repos/streamlit/streamlit",
        json=mock_metrics,
        status_code=200,
    )

    from src.processing.service import GitHubAnalyticsService

    with GitHubClient(token="mock_token") as client:
        service = GitHubAnalyticsService(client)
        metrics = service.get_metrics("streamlit", "streamlit")

    assert metrics.stargazers_count == 1000
    assert metrics.forks_count == 200
    assert metrics.open_issues_count == 50
    print("UAT-C02-01: Successfully retrieved mocked metrics via Service.")
    return client, metrics, mock_metrics, service, GitHubAnalyticsService


@app.cell
def __(GitHubClient, RepositoryNotFoundError, httpx_mock):
    # Scenario: UAT-C02-02 Graceful Error Translation (404)
    httpx_mock.add_response(
        url="https://api.github.com/repos/invalid-owner/invalid-repo",
        status_code=404,
    )

    try:
        with GitHubClient(token="mock_token") as client2:
            client2.get_repository_metrics("invalid-owner", "invalid-repo")
        pytest.fail("Should have raised RepositoryNotFoundError")
    except RepositoryNotFoundError:
        print("UAT-C02-02: Successfully handled 404 and translated to RepositoryNotFoundError.")
    return (client2,)


if __name__ == "__main__":
    app.run()

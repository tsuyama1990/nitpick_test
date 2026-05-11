import marimo

__generated_with = "0.4.0"
app = marimo.App()


@app.cell
def __():
    import sys
    from pathlib import Path

    project_root = str(Path(__file__).parent.parent.parent.resolve())
    if project_root not in sys.path:
        sys.path.append(project_root)
    return project_root, sys, Path


@app.cell
def __(project_root, sys):
    import pytest
    from httpx import Request, Response
    from pytest_httpx import HTTPXMock

    from src.domain_models.exceptions import RateLimitExceededError, RepositoryNotFoundError
    from src.ingestion.github_client import GitHubClient

    return (
        pytest,
        HTTPXMock,
        GitHubClient,
        RepositoryNotFoundError,
        RateLimitExceededError,
        Request,
        Response,
    )


@app.cell
def __(GitHubClient, HTTPXMock, RepositoryNotFoundError):
    import httpx
    from pytest_httpx import _HTTPXMockOptions

    options = _HTTPXMockOptions()
    mock_httpx = HTTPXMock(options=options)

    # UAT-C02-01 Successful Data Retrieval
    mock_httpx.add_response(
        url="https://api.github.com/repos/streamlit/streamlit",
        json={"stargazers_count": 30000, "forks_count": 2500, "open_issues_count": 500},
    )

    # Mock httpx.Client.send
    original_send = httpx.Client.send

    def mocked_send(self, request, **kwargs):
        res = mock_httpx._handle_request(request=request)
        res.request = request
        res.read()
        return res

    httpx.Client.send = mocked_send

    client = GitHubClient()
    result = client.get_repository_metrics("streamlit", "streamlit")
    print(f"UAT-C02-01: Fetched Metrics: {result}")

    assert result["stargazers_count"] == 30000

    # UAT-C02-02 Graceful Error Translation
    mock_httpx.reset()
    mock_httpx.add_response(
        url="https://api.github.com/repos/invalid-owner/invalid-repo", status_code=404
    )

    try:
        client.get_repository_metrics("invalid-owner", "invalid-repo")
        msg = "Should have raised RepositoryNotFoundError"
        raise AssertionError(msg)
    except RepositoryNotFoundError:
        print("UAT-C02-02: Successfully caught RepositoryNotFoundError")

    # restore send
    httpx.Client.send = original_send
    return client, mock_httpx, options, original_send, mocked_send, result


if __name__ == "__main__":
    app.run()

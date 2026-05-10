import marimo

__generated_with = "0.23.5"
app = marimo.App(width="medium")


@app.cell
def __():
    import sys
    from pathlib import Path

    # dynamically append the project root to sys.path
    project_root = str(Path(__file__).parent.parent.parent.resolve())
    if project_root not in sys.path:
        sys.path.append(project_root)

    from pytest_httpx import HTTPXMock
    from pytest_httpx._httpx_mock import _HTTPXMockOptions

    from src.domain.exceptions import RepositoryNotFoundError
    from src.ingestion.github_client import GitHubClient

    # We must patch httpx client with httpx_mock for our mock UAT tests
    return HTTPXMock, GitHubClient, RepositoryNotFoundError, _HTTPXMockOptions


@app.cell
def __(HTTPXMock, GitHubClient, _HTTPXMockOptions):
    import httpx

    # Initialize the HTTPXMock directly
    httpx_mock = HTTPXMock(options=_HTTPXMockOptions())

    # GIVEN
    client = GitHubClient(token="mock_token")
    mock_response = {
        "stargazers_count": 100,
        "forks_count": 50,
        "open_issues_count": 10,
    }
    httpx_mock.add_response(
        url="https://api.github.com/repos/streamlit/streamlit",
        json=mock_response,
        status_code=200,
    )

    # WHEN
    # Use httpx_mock to patch the specific client
    def patched_send(request: httpx.Request, *args, **kwargs) -> httpx.Response:
        # For HTTPXMock >= 0.30
        class DummyTransport:
            def handle_request(self, req):
                raise NotImplementedError()

        res = httpx_mock._handle_request(request=request, real_transport=DummyTransport())
        res.request = request
        res.read()
        return res

    client.client.send = patched_send

    metrics = client.get_repository_metrics("streamlit", "streamlit")

    # THEN
    assert metrics == mock_response
    assert metrics["stargazers_count"] == 100

    print("UAT-C02-01: Successful Data Retrieval Passed")
    return client, httpx_mock, patched_send


@app.cell
def __(client, httpx_mock, patched_send, RepositoryNotFoundError):
    # Setup for 404
    httpx_mock.reset()
    httpx_mock.add_response(
        url="https://api.github.com/repos/invalid-owner/invalid-repo",
        status_code=404,
    )

    try:
        client.get_repository_metrics("invalid-owner", "invalid-repo")
        assert False, "Should have raised RepositoryNotFoundError"
    except RepositoryNotFoundError:
        print("UAT-C02-02: Graceful Error Translation Passed (404 Not Found)")


if __name__ == "__main__":
    app.run()

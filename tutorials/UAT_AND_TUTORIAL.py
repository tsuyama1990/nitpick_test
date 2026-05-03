from typing import Any

import marimo

__generated_with = "0.2.0"
app = marimo.App()


@app.cell
def __imports() -> Any:
    import os

    import httpx
    import pytest
    import respx

    from src.domain_models import (
        AuthenticationError,
        RepositoryMetadata,
        RepositoryNotFoundError,
    )
    from src.ingestion.github_client import GitHubClient

    return (
        AuthenticationError,
        GitHubClient,
        RepositoryMetadata,
        RepositoryNotFoundError,
        httpx,
        os,
        pytest,
        respx,
    )


@app.cell
def __scenario_1(GitHubClient: Any, RepositoryMetadata: Any, httpx: Any, respx: Any) -> Any:
    # Scenario ID: C01-01 - Successful Data Extraction
    # We use respx mock here to ensure tests run smoothly without actual tokens.
    mock_response = {
        "name": "streamlit",
        "owner": {"login": "streamlit"},
        "stargazers_count": 30000,
        "forks_count": 5000,
        "open_issues_count": 200,
    }
    with respx.mock:
        respx.get("https://api.github.com/repos/streamlit/streamlit").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        client = GitHubClient()
        repo = client.fetch_repository_metadata("streamlit", "streamlit")
        assert isinstance(repo, RepositoryMetadata)
        print(f"Scenario 1 Success: Fetched metadata for {repo.name}")
    return


@app.cell
def __scenario_2(
    GitHubClient: Any, RepositoryNotFoundError: Any, httpx: Any, pytest: Any, respx: Any
) -> Any:
    # Scenario ID: C01-02 - Error Handling for Invalid Repositories
    with respx.mock:
        respx.get("https://api.github.com/repos/invalid/repo").mock(
            return_value=httpx.Response(404)
        )
        client = GitHubClient()
        with pytest.raises(RepositoryNotFoundError):
            client.fetch_repository_metadata("invalid", "repo")
        print("Scenario 2 Success: Handled 404 correctly")
    return


@app.cell
def __scenario_3(
    AuthenticationError: Any, GitHubClient: Any, httpx: Any, pytest: Any, respx: Any
) -> Any:
    # Scenario ID: C01-03 - Authentication Failure Handling
    with respx.mock:
        respx.get("https://api.github.com/repos/streamlit/streamlit").mock(
            return_value=httpx.Response(401)
        )
        client = GitHubClient()
        with pytest.raises(AuthenticationError):
            client.fetch_repository_metadata("streamlit", "streamlit")
        print("Scenario 3 Success: Handled Authentication Failure correctly")
    return


if __name__ == "__main__":
    app.run()

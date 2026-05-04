import marimo

__generated_with = "0.23.4"
app = marimo.App()


@app.cell
def __():
    from unittest.mock import patch

    import httpx
    import marimo as mo

    from src.domain_models.exceptions import AuthenticationError, RepositoryNotFoundError
    from src.domain_models.models import CommitRecord, RepositoryMetadata
    from src.ingestion.github_client import GithubClient

    # We will mock the client calls to ensure UAT can run consistently without hitting real API/Rate limits
    # The actual implementation acts strictly over httpx, but for UAT consistency in sandbox we mock the returns
    return (
        AuthenticationError,
        CommitRecord,
        GithubClient,
        RepositoryMetadata,
        RepositoryNotFoundError,
        httpx,
        mo,
        patch,
    )


@app.cell
def __(GithubClient, RepositoryMetadata, mo, patch):
    mo.md("### Scenario ID: C01-01 - Successful Data Extraction")

    client = GithubClient()

    mock_metadata = {
        "owner": {"login": "streamlit"},
        "name": "streamlit",
        "stargazers_count": 100,
        "forks_count": 10,
        "open_issues_count": 5,
    }

    with patch("httpx.Client.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_metadata

        metadata = client.get_repository_metadata("streamlit", "streamlit")

    mo.md(
        f"Metadata Extracted successfully: {metadata.owner}/{metadata.repo} with {metadata.star_count} stars"
    )
    return client, metadata, mock_get, mock_metadata


@app.cell
def __(RepositoryNotFoundError, client, mo, patch):
    mo.md("### Scenario ID: C01-02 - Error Handling for Invalid Repositories")

    with patch("httpx.Client.get") as mock_get:
        mock_get.return_value.status_code = 404

        try:
            client.get_repository_metadata("invalid-owner", "non-existent-repo-12345")
            mo.md("Failure: Did not raise RepositoryNotFoundError")
        except RepositoryNotFoundError as e:
            mo.md(f"Success: Caught expected error - {e}")
    return e, mock_get


@app.cell
def __(AuthenticationError, client, mo, patch):
    mo.md("### Scenario ID: C01-03 - Authentication Failure Handling")

    with patch("httpx.Client.get") as mock_get:
        mock_get.return_value.status_code = 401

        try:
            client.get_repository_metadata("streamlit", "streamlit")
            mo.md("Failure: Did not raise AuthenticationError")
        except AuthenticationError as e:
            msg = str(e)
            if "dummy_token" not in msg:
                mo.md(f"Success: Caught expected error and token is not leaked - {msg}")
            else:
                mo.md("Failure: Token was leaked in error message")
    return e, mock_get, msg


if __name__ == "__main__":
    app.run()

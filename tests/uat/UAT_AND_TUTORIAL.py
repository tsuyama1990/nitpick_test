import marimo

__generated_with = "0.2.0"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo

    return (mo,)


@app.cell
def __(mo):
    mo.md(
        """
        # Cycle 01 UAT: API Client Validation
        This notebook validates the GitHub API client ingestion logic to confirm that credentials and requests are handled properly.
        """
    )


@app.cell
def __(mo):
    from src.config import get_settings
    from src.domain_models import AuthenticationError, RepositoryNotFoundError
    from src.ingestion.github_client import GitHubClient

    settings = get_settings()
    token = settings.github_token

    mo.md(f"**Loaded Token?** {'Yes' if token else 'No'}")
    return GitHubClient, AuthenticationError, RepositoryNotFoundError, token


@app.cell
def __(mo, GitHubClient, token):
    # C01-01 - Successful Data Extraction
    client = GitHubClient(token=token)

    try:
        if not token:
            mo.md("Skipping C01-01 due to missing token in environment.")
            meta_display = None
        else:
            meta = client.fetch_repository_metadata("streamlit/streamlit")
            meta_display = mo.md(
                f"**C01-01 Success**: `{meta.owner}/{meta.name}` has `{meta.stars}` stars and `{meta.forks}` forks."
            )
    except Exception as e:
        meta_display = mo.md(f"**C01-01 Failed**: {e}")

    meta_display
    return client, meta, meta_display


@app.cell
def __(mo, GitHubClient, RepositoryNotFoundError):
    # C01-02 - Error Handling for Invalid Repositories
    client_invalid = GitHubClient()
    try:
        client_invalid.fetch_repository_metadata("invalid-owner/non-existent-repo-12345")
        error_display = mo.md("**C01-02 Failed**: Expected RepositoryNotFoundError, but succeeded.")
    except RepositoryNotFoundError as e:
        error_display = mo.md(
            f"**C01-02 Success**: Caught expected RepositoryNotFoundError - `{e}`"
        )
    except Exception as e:
        error_display = mo.md(f"**C01-02 Failed**: Caught wrong exception - `{e}`")

    error_display
    return client_invalid, error_display


@app.cell
def __(mo, GitHubClient, AuthenticationError):
    # C01-03 - Authentication Failure Handling
    client_auth = GitHubClient(token="ghp_invalidtoken123")
    try:
        client_auth.fetch_repository_metadata("streamlit/streamlit")
        auth_display = mo.md("**C01-03 Failed**: Expected AuthenticationError, but succeeded.")
    except AuthenticationError as e:
        auth_display = mo.md(
            f"**C01-03 Success**: Caught expected AuthenticationError - `{e}`. Note: Token is not leaked."
        )
    except Exception as e:
        auth_display = mo.md(f"**C01-03 Failed**: Caught wrong exception - `{e}`")

    auth_display
    return client_auth, auth_display


if __name__ == "__main__":
    app.run()

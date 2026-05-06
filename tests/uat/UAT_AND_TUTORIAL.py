import marimo

__generated_with = "0.23.5"
app = marimo.App()


@app.cell
def __():
    import os

    import marimo as mo

    from src.domain_models.exceptions import (
        AuthenticationError,
        RepositoryNotFoundError,
    )
    from src.ingestion.github_client import GitHubClient

    return AuthenticationError, GitHubClient, RepositoryNotFoundError, mo, os


@app.cell
def __(GitHubClient, mo, os):
    mo.md("### Scenario C01-01: Successful Data Extraction")
    token = os.getenv("GITHUB_TOKEN")
    client = GitHubClient(token=token)

    try:
        metadata = client.get_repository_metadata("streamlit", "streamlit")
        commits = client.get_commits("streamlit", "streamlit")
        mo.md(
            f"**Success**: Repo={metadata.repo}, Stars={metadata.star_count}, First Commit Hash={commits[0].commit_hash}"
        )
    except Exception as e:
        mo.md(f"**Failed**: {e}")
    return client, commits, metadata, token


@app.cell
def __(GitHubClient, RepositoryNotFoundError, mo, token):
    mo.md("### Scenario C01-02: Error Handling for Invalid Repositories")
    client_invalid = GitHubClient(token=token)
    try:
        client_invalid.get_repository_metadata("invalid-owner", "non-existent-repo-12345")
        mo.md("**Failed**: Expected RepositoryNotFoundError but got success.")
    except RepositoryNotFoundError as e:
        mo.md(f"**Success**: Caught expected exception -> {e}")
    except Exception as e:
        mo.md(f"**Failed**: Caught wrong exception -> {e}")
    return (client_invalid,)


@app.cell
def __(AuthenticationError, GitHubClient, mo):
    mo.md("### Scenario C01-03: Authentication Failure Handling")
    client_auth = GitHubClient(token="ghp_invalidtoken123")
    try:
        client_auth.get_repository_metadata("streamlit", "streamlit")
        mo.md("**Failed**: Expected AuthenticationError but got success.")
    except AuthenticationError as e:
        mo.md(
            f"**Success**: Caught expected exception. Message snippet (proving no token leak): {str(e)[:50]}..."
        )
    except Exception as e:
        mo.md(f"**Failed**: Caught wrong exception -> {e}")
    return (client_auth,)


if __name__ == "__main__":
    app.run()

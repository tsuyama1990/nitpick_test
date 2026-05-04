import marimo

__generated_with = "0.2.0"
app = marimo.App()


@app.cell
def __():
    import os
    import marimo as mo
    from src.ingestion.github_client import GitHubClient
    from src.domain_models import AuthenticationError, RepositoryNotFoundError

    # We load standard variables from .env if present for successful tests
    from dotenv import load_dotenv

    load_dotenv()
    return AuthenticationError, GitHubClient, RepositoryNotFoundError, load_dotenv, mo, os


@app.cell
def __(GitHubClient, mo, os):
    mo.md(
        """
        # CYCLE 01 UAT: API Client Validation

        This notebook verifies the exact scenarios defined in `UAT.md`.
        """
    )
    return


@app.cell
def __(GitHubClient, mo, os):
    mo.md("## Scenario ID: C01-01 - Successful Data Extraction")
    return


@app.cell
def __(GitHubClient, os):
    # Verify we can extract repository metadata and commits successfully
    # Ensure you have a valid GITHUB_TOKEN in your environment.
    _token = os.getenv("GITHUB_TOKEN", "")
    _client = GitHubClient(token=_token)

    try:
        repo_metadata = _client.get_repository_metadata("streamlit/streamlit")
        recent_commits = _client.get_recent_commits("streamlit/streamlit")

        success_result = {
            "Repo Name": repo_metadata.repo_name,
            "Owner": repo_metadata.owner,
            "Stars": repo_metadata.star_count,
            "Forks": repo_metadata.fork_count,
            "Commit Count (limit 100)": len(recent_commits),
            "First Commit Author": recent_commits[0].author_name if recent_commits else "None",
        }
    except Exception as e:
        success_result = f"Failed: {e}"

    success_result
    return recent_commits, repo_metadata, success_result


@app.cell
def __(mo):
    mo.md("## Scenario ID: C01-02 - Error Handling for Invalid Repositories")
    return


@app.cell
def __(GitHubClient, RepositoryNotFoundError, os):
    # Verify that a 404 response raises the custom RepositoryNotFoundError
    _token = os.getenv("GITHUB_TOKEN", "")
    _client_not_found = GitHubClient(token=_token)

    try:
        _client_not_found.get_repository_metadata("invalid-owner/non-existent-repo-12345")
        not_found_result = "Failed: Expected an exception, but got a successful response."
    except RepositoryNotFoundError as e:
        not_found_result = f"Success: Caught expected error -> {e}"
    except Exception as e:
        not_found_result = f"Failed: Caught unexpected error -> {e}"

    not_found_result
    return (not_found_result,)


@app.cell
def __(mo):
    mo.md("## Scenario ID: C01-03 - Authentication Failure Handling")
    return


@app.cell
def __(AuthenticationError, GitHubClient):
    # Verify that invalid tokens securely throw AuthenticationError without leaking the token
    _invalid_token = "ghp_invalidtoken123"
    _client_auth_fail = GitHubClient(token=_invalid_token)

    try:
        _client_auth_fail.get_repository_metadata("streamlit/streamlit")
        auth_fail_result = "Failed: Expected an authentication error."
    except AuthenticationError as e:
        _error_msg = str(e)
        if _invalid_token in _error_msg:
            auth_fail_result = "Failed: Token leaked in error message!"
        else:
            auth_fail_result = f"Success: Caught expected error securely -> {_error_msg}"
    except Exception as e:
        auth_fail_result = f"Failed: Caught unexpected error -> {e}"

    auth_fail_result
    return (auth_fail_result,)


if __name__ == "__main__":
    app.run()

import marimo

__generated_with = "0.23.4"
app = marimo.App()


@app.cell
def setup_scenario(mo): # type: ignore
    mo.md(
        """
        # CYCLE 01 UAT: API Client Validation

        This interactive notebook validates the core GitHub Client functionality for successful data retrieval, invalid repository handling, and authentication error handling.
        """
    )


@app.cell
def load_deps(): # type: ignore
    from src.config import Settings
    from src.domain_models.exceptions import AuthenticationError, RepositoryNotFoundError
    from src.ingestion.github_client import GitHubClient

    # Helper function to inject settings for testing
    def get_test_client(token=""):
        # We explicitly inject a token for these test scenarios, avoiding loading from .env if we want to force failure
        test_settings = Settings(github_token=token)  # type: ignore[call-arg]
        return GitHubClient(settings=test_settings)

    return (
        AuthenticationError,
        GitHubClient,
        RepositoryNotFoundError,
        Settings,
        get_test_client,
    )


@app.cell
def s1_desc(mo): # type: ignore
    mo.md(
        """
        ### Scenario ID: C01-01 - Successful Data Extraction

        Testing successful extraction of metadata and commits. Note: This assumes you have a valid token in your `.env` file, but we will test error handling explicitly.
        """
    )


@app.cell
def s1_exec(GitHubClient, Settings, mo): # type: ignore # noqa: N803
    try:
        # Assuming .env is valid, we test the successful case
        valid_client = GitHubClient(settings=Settings())  # type: ignore[call-arg]
        metadata = valid_client.get_repository_metadata("streamlit", "streamlit")
        commits = valid_client.get_recent_commits("streamlit", "streamlit")

        scenario_1_status = "Success"
        scenario_1_details = f"Retrieved metadata for {metadata.owner}/{metadata.repo_name} with {metadata.star_count} stars. Found {len(commits)} commits."
    except Exception as e:
        scenario_1_status = "Failed"
        scenario_1_details = f"Error: {e}"
        commits = None
        metadata = None
        valid_client = None

    mo.md(f"**Scenario 1 Status:** {scenario_1_status}\n\n**Details:** {scenario_1_details}")
    return commits, metadata, scenario_1_details, scenario_1_status, valid_client


@app.cell
def s2_desc(mo): # type: ignore
    mo.md(
        """
        ### Scenario ID: C01-02 - Error Handling for Invalid Repositories

        Testing error handling when the repository does not exist (404). We expect a `RepositoryNotFoundError`.
        """
    )


@app.cell
def s2_exec(RepositoryNotFoundError, mo): # type: ignore # noqa: N803
    # Using the client (even if token is empty, a 404 should be raised if repo is not found, though GitHub may return 404 for unauthenticated access too depending on the repo).
    # To reliably test 404, we use a valid-looking but nonexistent repo. If token is invalid, it might fail Scenario 3 first.

    try:
        # Assuming we have a valid token from Settings(), but for this specific test we just want to ensure it handles 404. We'll try to fetch with a dummy valid-looking token if none is present to trigger auth or 404. Let's just use the valid client if possible, or a dummy token to see if it catches the right error.
        from src.config import Settings
        from src.ingestion.github_client import GitHubClient

        test_client = GitHubClient(settings=Settings())  # type: ignore[call-arg]
        test_client.get_repository_metadata(
            "invalid-owner-123456789", "non-existent-repo-12345"
        )
        scenario_2_status = "Failed"
        scenario_2_details = "Expected RepositoryNotFoundError, but succeeded."
    except RepositoryNotFoundError as e:
        scenario_2_status = "Success"
        scenario_2_details = f"Caught expected RepositoryNotFoundError: {e}"
        test_client = None
    except Exception as e:
        scenario_2_status = "Failed"
        scenario_2_details = f"Caught unexpected error: {type(e).__name__}: {e}"
        test_client = None

    mo.md(f"**Scenario 2 Status:** {scenario_2_status}\n\n**Details:** {scenario_2_details}")
    return scenario_2_details, scenario_2_status, test_client


@app.cell
def s3_desc(mo): # type: ignore
    mo.md(
        """
        ### Scenario ID: C01-03 - Authentication Failure Handling

        Testing resilience against invalid tokens (401/403). We expect an `AuthenticationError` and verify the token is not leaked.
        """
    )


@app.cell
def s3_exec(AuthenticationError, get_test_client, mo): # type: ignore # noqa: N803
    invalid_token = "ghp_invalidtoken123_test_leak" # noqa: S105
    invalid_client = get_test_client(token=invalid_token)

    try:
        invalid_client.get_repository_metadata("streamlit", "streamlit")
        scenario_3_status = "Failed"
        scenario_3_details = "Expected AuthenticationError, but succeeded."
        error_message = ""
    except AuthenticationError as e:
        error_message = str(e)
        if invalid_token in error_message:
            scenario_3_status = "Failed"
            scenario_3_details = "AuthenticationError raised, but the token was leaked in the error message!"
        else:
            scenario_3_status = "Success"
            scenario_3_details = f"Caught expected AuthenticationError without leaking token: {e}"
    except Exception as e:
        scenario_3_status = "Failed"
        scenario_3_details = f"Caught unexpected error: {type(e).__name__}: {e}"
        error_message = ""

    mo.md(f"**Scenario 3 Status:** {scenario_3_status}\n\n**Details:** {scenario_3_details}")
    return (
        error_message,
        invalid_client,
        invalid_token,
        scenario_3_details,
        scenario_3_status,
    )


if __name__ == "__main__":
    app.run()

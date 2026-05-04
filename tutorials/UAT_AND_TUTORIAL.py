import marimo

__generated_with = "0.23.4"
app = marimo.App()


@app.cell
def __():
    import os

    import marimo as mo

    from src.config import AppConfig
    from src.domain_models import AuthenticationError, RepositoryNotFoundError
    from src.ingestion.github_client import GithubClient

    # Check if a real token is available
    real_token = os.environ.get("GITHUB_TOKEN")
    if not real_token or real_token == "mock_token_for_tests":  # noqa: S105
        mo.md(
            "⚠️ **Warning**: No real GITHUB_TOKEN set. The following tests will use dummy tokens and will demonstrate error handling, but success scenarios will fail."
        )
    else:
        mo.md("✅ Real GITHUB_TOKEN found.")
    return AppConfig, AuthenticationError, GithubClient, RepositoryNotFoundError, mo, os, real_token


@app.cell
def __(AppConfig, GithubClient, mo, real_token):
    mo.md("### Scenario ID: C01-01 - Successful Data Extraction")
    if real_token and real_token != "mock_token_for_tests":  # noqa: S105
        _config = AppConfig(github_token=real_token)
        _client = GithubClient(_config)
        _meta = _client.fetch_repository_metadata("streamlit", "streamlit")
        _commits = _client.fetch_latest_commits("streamlit", "streamlit", limit=5)

        mo.output.append(mo.md(f"**Metadata**: {_meta}"))
        mo.output.append(
            mo.md(f"**Latest Commit**: {_commits[0].sha} by {_commits[0].author_name}")
        )
    else:
        mo.output.append(mo.md("*Skipped because no real token.*"))


@app.cell
def __(AppConfig, GithubClient, RepositoryNotFoundError, mo, real_token):
    mo.md("### Scenario ID: C01-02 - Error Handling for Invalid Repositories")
    if real_token and real_token != "mock_token_for_tests":  # noqa: S105
        _config = AppConfig(github_token=real_token)
        _client = GithubClient(_config)
        try:
            _client.fetch_repository_metadata("invalid-owner", "non-existent-repo-12345")
            mo.output.append(mo.md("❌ Expected RepositoryNotFoundError, but got success."))
        except RepositoryNotFoundError as e:
            mo.output.append(mo.md(f"✅ Successfully caught expected error: {e}"))


@app.cell
def __(AppConfig, AuthenticationError, GithubClient, mo):
    mo.md("### Scenario ID: C01-03 - Authentication Failure Handling")

    _bad_config = AppConfig(github_token="ghp_invalidtoken123")
    _bad_client = GithubClient(_bad_config)
    try:
        _bad_client.fetch_repository_metadata("streamlit", "streamlit")
        mo.output.append(mo.md("❌ Expected AuthenticationError, but got success."))
    except AuthenticationError as e:
        mo.output.append(mo.md(f"✅ Successfully caught expected error: {type(e).__name__}"))
        if "ghp_invalidtoken123" in str(e):
            mo.output.append(mo.md("❌ CRITICAL: Token leaked in error message!"))
        else:
            mo.output.append(mo.md("✅ Token was safely redacted from error message."))


if __name__ == "__main__":
    app.run()

import marimo

__generated_with = "0.2.1"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo

    from src.config import get_settings
    from src.domain_models.exceptions import AuthenticationError, RepositoryNotFoundError
    from src.ingestion.github_client import GitHubClient

    return AuthenticationError, GitHubClient, RepositoryNotFoundError, get_settings, mo


@app.cell
def __(mo):
    mo.md("# CYCLE 01 UAT: API Client Validation")


@app.cell
def __(GitHubClient, get_settings, mo):
    mo.md("### Scenario ID: C01-01 - Successful Data Extraction")
    settings = get_settings()
    if settings.GITHUB_TOKEN:
        client = GitHubClient(token=settings.GITHUB_TOKEN)
        repo = client.fetch_repository_metadata("streamlit", "streamlit")
        commits = client.fetch_commit_history("streamlit", "streamlit")
        mo.output.append(mo.md(f"**Repository**: {repo.name} - Stars: {repo.stargazers_count}"))
        mo.output.append(mo.md(f"**Commits Fetched**: {len(commits)}"))
        mo.output.append(mo.md(f"**Latest Commit**: {commits[0].sha} by {commits[0].author_name}"))
    else:
        mo.output.append(mo.md("**SKIPPED**: No GITHUB_TOKEN provided."))
    return client, commits, repo, settings


@app.cell
def __(GitHubClient, RepositoryNotFoundError, mo, settings):
    mo.md("### Scenario ID: C01-02 - Error Handling for Invalid Repositories")
    if settings.GITHUB_TOKEN:
        client2 = GitHubClient(token=settings.GITHUB_TOKEN)
        try:
            client2.fetch_repository_metadata("invalid-owner", "non-existent-repo-12345")
            mo.output.append(mo.md("FAILED: Exception not raised!"))
        except RepositoryNotFoundError as e:
            mo.output.append(mo.md(f"**SUCCESS**: Caught expected Exception: `{type(e).__name__}`"))
    else:
        mo.output.append(mo.md("**SKIPPED**: No GITHUB_TOKEN provided."))
    return (client2,)


@app.cell
def __(AuthenticationError, GitHubClient, mo):
    mo.md("### Scenario ID: C01-03 - Authentication Failure Handling")
    client_invalid = GitHubClient(token="ghp_invalidtoken123")
    try:
        client_invalid.fetch_repository_metadata("streamlit", "streamlit")
        mo.output.append(mo.md("FAILED: Exception not raised!"))
    except AuthenticationError as e:
        if "ghp_invalidtoken123" not in str(e):
            mo.output.append(
                mo.md("**SUCCESS**: Caught `AuthenticationError` and token is NOT in message!")
            )
        else:
            mo.output.append(mo.md("**FAILED**: Caught `AuthenticationError` but token leaked!"))
    return (client_invalid,)


if __name__ == "__main__":
    app.run()

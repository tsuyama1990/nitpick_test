import marimo

__generated_with = "0.8.20"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo

    from src.domain_models.config import get_config
    from src.domain_models.exceptions import (
        AuthenticationError,
        GitHubClientError,
        RateLimitError,
        RepositoryNotFoundError,
    )
    from src.ingestion.github_client import GitHubClient

    return (
        GitHubClient,
        GitHubClientError,
        AuthenticationError,
        RateLimitError,
        RepositoryNotFoundError,
        get_config,
        mo,
    )


@app.cell
def __(
    AuthenticationError,
    GitHubClient,
    GitHubClientError,
    RateLimitError,
    RepositoryNotFoundError,
    get_config,
    mo,
):
    mo.md(
        """
        # CYCLE 01 UAT: API Client Validation

        This notebook verifies the GitHub API Client implementation.
        Ensure you have a valid `.env` file with `GITHUB_TOKEN`.
        """
    )

    try:
        config = get_config()
        client = GitHubClient(config)
        mo.md("✅ Configuration and Client initialized successfully.")
    except Exception as e:
        mo.md(f"❌ Failed to initialize config/client: {e}")
    return client, config


@app.cell
def __(client, mo):
    mo.md("## Scenario ID: C01-01 - Successful Data Extraction")

    try:
        metadata = client.get_repository_metadata("streamlit", "streamlit")
        commits = client.get_commits("streamlit", "streamlit")
        output_01 = mo.md(
            f"✅ **Success**: Retrieved metadata for {metadata.owner}/{metadata.repo}.\\n"
            f"- Stars: {metadata.stargazers_count}\\n"
            f"- Forks: {metadata.forks_count}\\n"
            f"- Open Issues: {metadata.open_issues_count}\\n\\n"
            f"Retrieved {len(commits)} commits.\\n"
            f"Latest commit: {commits[0].sha} by {commits[0].author_name} at {commits[0].date}."
        )
    except Exception as e:
        output_01 = mo.md(f"❌ **Failed**: {e}")

    output_01
    return commits, metadata, output_01


@app.cell
def __(RepositoryNotFoundError, client, mo):
    mo.md("## Scenario ID: C01-02 - Error Handling for Invalid Repositories")

    try:
        client.get_repository_metadata("invalid-owner", "non-existent-repo-12345")
        output_02 = mo.md("❌ **Failed**: Expected RepositoryNotFoundError but request succeeded.")
    except RepositoryNotFoundError as e:
        output_02 = mo.md(f"✅ **Success**: Correctly caught RepositoryNotFoundError: {e}")
    except Exception as e:
        output_02 = mo.md(f"❌ **Failed**: Caught wrong exception type: {e}")

    output_02
    return (output_02,)


@app.cell
def __(AuthenticationError, GitHubClient, mo, config):
    from src.domain_models.config import AppConfig

    mo.md("## Scenario ID: C01-03 - Authentication Failure Handling")

    try:
        bad_config = AppConfig(github_token="ghp_invalidtoken123")  # noqa: S106
        bad_client = GitHubClient(bad_config)
        bad_client.get_repository_metadata("streamlit", "streamlit")
        output_03 = mo.md("❌ **Failed**: Expected AuthenticationError but request succeeded.")
    except AuthenticationError as e:
        err_msg = str(e)
        if "ghp_invalidtoken123" not in err_msg:
            output_03 = mo.md(
                f"✅ **Success**: Caught AuthenticationError without leaking token. Message: {err_msg}"
            )
        else:
            output_03 = mo.md(f"❌ **Failed**: Token leaked in error message: {err_msg}")
    except Exception as e:
        output_03 = mo.md(f"❌ **Failed**: Caught wrong exception type: {e}")

    output_03
    return bad_client, bad_config, err_msg, output_03


if __name__ == "__main__":
    app.run()

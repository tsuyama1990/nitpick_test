import marimo

__generated_with = "0.23.5"
app = marimo.App()


@app.cell
def __():
    import marimo as mo

    return (mo,)


@app.cell
def __(mo):
    mo.md("# UAT Scenario C01-01")


@app.cell
def __(mo):
    mo.md("## Scenario C01-01: Successful Data Extraction")


@app.cell
def __():
    import os

    from src.domain_models.github import CommitRecord, RepositoryMetadata
    from src.ingestion.github_client import GitHubClient

    client = GitHubClient(token=os.getenv("GITHUB_TOKEN"))
    metadata = client.fetch_repository_metadata("streamlit", "streamlit")
    assert isinstance(metadata, RepositoryMetadata)
    print(f"Successfully fetched metadata: {metadata.name} with {metadata.star_count} stars.")

    commits = client.fetch_commit_history("streamlit", "streamlit")
    assert len(commits) > 0
    assert isinstance(commits[0], CommitRecord)
    print(
        f"Successfully fetched {len(commits)} commits. Latest commit by {commits[0].author_name}."
    )
    return client, metadata, commits


@app.cell
def __(mo):
    mo.md("## Scenario C01-02: Error Handling for Invalid Repositories")


@app.cell
def __(client):
    from src.domain_models.exceptions import RepositoryNotFoundError

    try:
        client.fetch_repository_metadata("invalid-owner", "non-existent-repo-12345")
    except RepositoryNotFoundError as e:
        print(f"Successfully caught RepositoryNotFoundError: {e}")
    else:
        msg = "Expected RepositoryNotFoundError was not raised"
        raise AssertionError(msg)


@app.cell
def __(mo):
    mo.md("## Scenario C01-03: Authentication Failure Handling")


@app.cell
def __():
    from src.domain_models.exceptions import AuthenticationError
    from src.ingestion.github_client import GitHubClient

    dummy_token = "ghp_invalidtoken123"  # noqa: S105
    invalid_client = GitHubClient(token=dummy_token)
    try:
        invalid_client.fetch_repository_metadata("streamlit", "streamlit")
    except AuthenticationError as e:
        print(f"Successfully caught AuthenticationError: {e}")
        assert dummy_token not in str(e), "Secret token leaked in error message!"
    else:
        msg = "Expected AuthenticationError was not raised"
        raise AssertionError(msg)
    return (invalid_client,)


if __name__ == "__main__":
    app.run()

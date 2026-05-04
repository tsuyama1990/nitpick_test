import marimo

__generated_with = "0.23.4"
app = marimo.App(width="medium")


@app.cell
def __():
    import os

    import pytest
    from pydantic import ValidationError

    from src.config import settings
    from src.domain_models.exceptions import (
        AuthenticationError,
        RepositoryNotFoundError,
    )
    from src.ingestion.github_client import GithubClient

    client = GithubClient(token=settings.github_token)
    return (
        AuthenticationError,
        GithubClient,
        RepositoryNotFoundError,
        ValidationError,
        client,
        os,
        pytest,
        settings,
    )


@app.cell
def __(client):
    print("Testing C01-01 - Successful Data Extraction")

    # Try fetch repository metadata
    try:
        repo = client.fetch_repository_metadata("streamlit/streamlit")
        print(f"Success! Repo: {repo.name}, Stars: {repo.star_count}, Forks: {repo.fork_count}")
    except Exception as e:
        print(f"Error fetching repo metadata: {e}")

    # Try fetch commits
    try:
        commits = client.fetch_commits("streamlit/streamlit")
        print(f"Success! Retrieved {len(commits)} commits.")
        if commits:
            print(f"Latest commit by {commits[0].author_name} at {commits[0].timestamp}")
    except Exception as e:
        print(f"Error fetching commits: {e}")
    return commits, repo


@app.cell
def __(RepositoryNotFoundError, client):
    print("Testing C01-02 - Error Handling for Invalid Repositories")
    try:
        client.fetch_repository_metadata("invalid-owner/non-existent-repo-12345")
        print("Failed: Should have raised RepositoryNotFoundError")
    except RepositoryNotFoundError as e:
        print(f"Success: Caught RepositoryNotFoundError: {e}")
    except Exception as e:
        print(f"Failed: Caught unexpected exception: {e}")


@app.cell
def __(AuthenticationError, GithubClient):
    print("Testing C01-03 - Authentication Failure Handling")
    invalid_client = GithubClient(token="ghp_invalidtoken123")
    try:
        invalid_client.fetch_repository_metadata("streamlit/streamlit")
        print("Failed: Should have raised AuthenticationError")
    except AuthenticationError as e:
        print(f"Success: Caught AuthenticationError: {e}")
        assert "ghp_invalidtoken123" not in str(e), "Token was leaked in error message!"
        print("Success: Token was not leaked.")
    except Exception as e:
        print(f"Failed: Caught unexpected exception: {e}")
    return invalid_client,


if __name__ == "__main__":
    app.run()

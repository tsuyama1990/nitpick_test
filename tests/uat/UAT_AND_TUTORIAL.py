import marimo

__generated_with = "0.2.0"
app = marimo.App()


@app.cell
def __():
    import marimo as mo

    from src.config import get_settings
    from src.domain_models import AuthenticationError, RepositoryNotFoundError
    from src.ingestion.github_client import GitHubClient

    return GitHubClient, get_settings, AuthenticationError, RepositoryNotFoundError, mo


@app.cell
def __(GitHubClient, get_settings, mo):
    settings = get_settings()
    # Provide token if any
    token = settings.GITHUB_TOKEN
    client = GitHubClient(token=token)

    if token:
        try:
            repo = client.get_repository_metadata("streamlit", "streamlit")
            mo.md(
                f"Successfully connected! Found repository: {repo.name} with {repo.stargazers_count} stars."
            )
        except Exception as e:
            mo.md(f"Error fetching repo: {e}")
    else:
        mo.md("No GITHUB_TOKEN configured. Provide one in .env to run live fetches.")
    return client, settings, token


@app.cell
def __(AuthenticationError, GitHubClient, mo):
    # Test authentication failure handling
    invalid_client = GitHubClient(token="ghp_invalidtoken123")
    try:
        invalid_client.get_repository_metadata("streamlit", "streamlit")
        auth_result = "Failed: Did not raise AuthenticationError."
    except AuthenticationError as e:
        if "ghp_invalidtoken123" not in str(e):
            auth_result = "Success: AuthenticationError raised safely without leaking token."
        else:
            auth_result = "Failed: Raised error but token leaked."
    except Exception as e:
        auth_result = f"Failed: Unexpected error type: {e}"
    mo.md(f"Auth test result: {auth_result}")
    return auth_result, invalid_client


@app.cell
def __(RepositoryNotFoundError, client, mo, token):
    if token:
        try:
            client.get_repository_metadata("invalid-owner", "non-existent-repo-12345")
            not_found_result = "Failed: Did not raise RepositoryNotFoundError."
        except RepositoryNotFoundError:
            not_found_result = "Success: RepositoryNotFoundError correctly raised."
    else:
        not_found_result = "Skipped missing token."
    mo.md(f"Not Found test result: {not_found_result}")
    return (not_found_result,)


if __name__ == "__main__":
    app.run()

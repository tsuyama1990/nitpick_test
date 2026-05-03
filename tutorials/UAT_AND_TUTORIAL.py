import marimo

__generated_with = "0.23.4"
app = marimo.App()


@app.cell
def __():
    import os

    import marimo as mo

    from src.config import get_settings
    from src.domain_models import AuthenticationError, RepositoryNotFoundError
    from src.ingestion.github_client import GitHubClient

    return AuthenticationError, GitHubClient, RepositoryNotFoundError, get_settings, mo, os


@app.cell
def __(get_settings, mo, os):
    # Try to load real token, otherwise set empty
    try:
        settings = get_settings()
        GITHUB_TOKEN = settings.github_token
        mode = "Real Mode"
    except Exception:
        GITHUB_TOKEN = ""
        mode = "Mock Mode (No Token Found)"

    mo.md(f"### Current Mode: {mode}")
    return GITHUB_TOKEN, mode, settings


@app.cell
def __(GITHUB_TOKEN, GitHubClient):
    client = GitHubClient(token=GITHUB_TOKEN)
    client
    return (client,)


@app.cell
def __(client, mo):
    target_owner = "streamlit"
    target_repo = "streamlit"

    mo.md(f"Fetching metadata for `{target_owner}/{target_repo}`...")
    return target_owner, target_repo


@app.cell
def __(client, mo, target_owner, target_repo):
    try:
        repo_metadata = client.get_repository_metadata(target_owner, target_repo)
        mo.md(
            f"**Success!** Repository: {repo_metadata.owner}/{repo_metadata.repo} | Stars: {repo_metadata.stars} | Forks: {repo_metadata.forks}"
        )
    except Exception as e:
        repo_metadata = None
        mo.md(f"**Error:** {e!s}")
    return (repo_metadata,)


@app.cell
def __(client, mo, target_owner, target_repo):
    try:
        commits = client.get_recent_commits(target_owner, target_repo, limit=5)
        mo.md(f"**Success!** Fetched {len(commits)} commits.")
        for c in commits:
            print(f"- {c.commit_hash[:7]}: {c.author_name} at {c.timestamp}")  # noqa: T201
    except Exception as e:
        commits = None
        mo.md(f"**Error:** {e!s}")
    return (commits,)


@app.cell
def __(RepositoryNotFoundError, client, mo):
    try:
        client.get_repository_metadata("invalid-owner", "non-existent-repo-12345")
        mo.md("**Failure:** Expected a RepositoryNotFoundError but succeeded.")
    except RepositoryNotFoundError:
        mo.md("**Success!** Caught RepositoryNotFoundError gracefully for invalid repo.")


if __name__ == "__main__":
    app.run()

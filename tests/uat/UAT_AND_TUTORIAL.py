import marimo

__generated_with = "0.23.5"
app = marimo.App(width="medium")


@app.cell
def __():
    import sys
    from pathlib import Path

    # Append project root to sys.path to allow imports from src
    root_dir = str(Path().cwd().absolute())
    if root_dir not in sys.path:
        sys.path.append(root_dir)
    return Path, root_dir, sys


@app.cell
def __(Path):
    from src.github_client import GitHubClient

    # Determine if we are in mock mode (CI without .env) or real mode (local dev with .env)
    env_exists = Path(".env").exists()
    return GitHubClient, env_exists


@app.cell
def __(GitHubClient, env_exists):
    import marimo as mo

    if env_exists:
        mo.md("### Running in LIVE mode (.env found).")
        client = GitHubClient()
        repo = client.get_repository_info("streamlit", "streamlit")
        commits = client.get_recent_commits("streamlit", "streamlit", limit=5)

        result_md = f"""
        **Repository:** {repo.full_name}
        - Stars: {repo.stargazers_count}
        - Forks: {repo.forks_count}
        - Open Issues: {repo.open_issues_count}

        **Recent Commits:**
        """
        for c in commits:
            result_md += f"- `{c.sha[:7]}`: {c.commit.message} (by {c.commit.author.name})\n"

        output = mo.md(result_md)
    else:
        output = mo.md("### Running in MOCK mode (no .env found). Skipping live API calls.")
    return client, commits, mo, output, repo, result_md


@app.cell
def __(output):
    output


if __name__ == "__main__":
    app.run()

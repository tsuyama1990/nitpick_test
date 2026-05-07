import os

import pytest

from src.ingestion import GitHubClient


@pytest.mark.live
def test_live_github_api_connection() -> None:
    # Skip if real token is not provided
    if not os.environ.get("GITHUB_TOKEN"):
        pytest.skip("No GITHUB_TOKEN provided for live test.")

    client = GitHubClient()

    # Test repository info
    repo_info = client.fetch_repository_info("streamlit", "streamlit")
    assert repo_info.stargazers_count > 0
    assert repo_info.forks_count > 0
    assert repo_info.open_issues_count >= 0

    # Test commits fetch
    commits = client.fetch_recent_commits("streamlit", "streamlit", limit=5)
    assert len(commits) == 5
    assert commits[0].author_name
    assert commits[0].date

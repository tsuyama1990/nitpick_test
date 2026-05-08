import os

import pytest

from src.ingestion.api_client import GitHubAPIClient


@pytest.mark.live
def test_live_github_api_repo_info() -> None:
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        pytest.skip("GITHUB_TOKEN not set")

    client = GitHubAPIClient()
    repo_info = client.get_repo_info("streamlit", "streamlit")

    assert repo_info.stargazers_count > 0
    assert repo_info.forks_count >= 0
    assert repo_info.open_issues_count >= 0


@pytest.mark.live
def test_live_github_api_commits() -> None:
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        pytest.skip("GITHUB_TOKEN not set")

    client = GitHubAPIClient()
    commits = client.get_recent_commits("streamlit", "streamlit", limit=5)

    assert len(commits) == 5
    assert commits[0].sha is not None
    assert commits[0].committer_name is not None
    assert commits[0].committer_date is not None


def test_dummy() -> None:
    assert True

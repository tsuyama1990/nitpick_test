import os

import pytest

from src.ingestion.github_client import GitHubClient


@pytest.mark.live
def test_live_get_repository_metadata() -> None:
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        pytest.skip("GITHUB_TOKEN not set for live testing")

    client = GitHubClient(token=token)
    repo = client.get_repository_metadata("streamlit/streamlit")

    assert repo.repo_name == "streamlit"
    assert repo.owner == "streamlit"
    assert repo.star_count > 0


@pytest.mark.live
def test_live_get_recent_commits() -> None:
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        pytest.skip("GITHUB_TOKEN not set for live testing")

    client = GitHubClient(token=token)
    commits = client.get_recent_commits("streamlit/streamlit")

    assert len(commits) > 0
    assert len(commits) <= 100
    assert commits[0].commit_hash

import os

import pytest

from src.ingestion.github_client import GitHubClient

pytestmark = pytest.mark.live


@pytest.mark.skipif(
    not os.environ.get("GITHUB_TOKEN"), reason="GITHUB_TOKEN is not set in the environment"
)
def test_live_github_api_metadata() -> None:
    client = GitHubClient()
    repo = client.fetch_repository_metadata("streamlit", "streamlit")
    assert repo.name == "streamlit"
    assert repo.owner == "streamlit"
    assert repo.stargazers_count > 0


@pytest.mark.skipif(
    not os.environ.get("GITHUB_TOKEN"), reason="GITHUB_TOKEN is not set in the environment"
)
def test_live_github_api_commits() -> None:
    client = GitHubClient()
    commits = client.fetch_latest_commits("streamlit", "streamlit", limit=5)
    assert len(commits) == 5
    assert commits[0].sha
    assert commits[0].author_name

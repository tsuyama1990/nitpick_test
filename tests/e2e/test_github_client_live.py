import pytest

from src.domain_models import Commit, Repository
from src.github_client import GitHubClient


@pytest.mark.live
def test_live_get_repository_info() -> None:
    """Live test against the real GitHub API. Requires a valid .env setup."""
    client = GitHubClient()
    repo = client.get_repository_info("streamlit", "streamlit")

    assert isinstance(repo, Repository)
    assert repo.name == "streamlit"
    assert repo.stargazers_count > 0


@pytest.mark.live
def test_live_get_recent_commits() -> None:
    """Live test against the real GitHub API. Requires a valid .env setup."""
    client = GitHubClient()
    commits = client.get_recent_commits("streamlit", "streamlit", limit=5)

    assert isinstance(commits, list)
    assert len(commits) > 0
    assert len(commits) <= 5
    assert isinstance(commits[0], Commit)
    assert commits[0].sha
    assert commits[0].commit.message

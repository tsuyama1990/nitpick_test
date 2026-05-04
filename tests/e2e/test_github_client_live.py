
import pytest

from src.config import get_settings
from src.ingestion.github_client import GitHubClient


@pytest.mark.live
def test_fetch_repository_metadata_live() -> None:
    settings = get_settings()
    if not settings.github_token:
        pytest.skip("GITHUB_TOKEN not found in environment, skipping live test.")

    client = GitHubClient(token=settings.github_token)
    repo = client.fetch_repository_metadata("streamlit", "streamlit")

    assert repo.name == "streamlit"
    assert repo.owner == "streamlit"
    assert repo.stargazers_count > 0
    assert repo.forks_count > 0


@pytest.mark.live
def test_fetch_commit_history_live() -> None:
    settings = get_settings()
    if not settings.github_token:
        pytest.skip("GITHUB_TOKEN not found in environment, skipping live test.")

    client = GitHubClient(token=settings.github_token)
    commits = client.fetch_commit_history("streamlit", "streamlit")

    assert len(commits) > 0
    assert commits[0].sha
    assert commits[0].author_name

import pytest

from src.ingestion.github_client import get_commits, get_repo_info


@pytest.mark.live
def test_live_github_api() -> None:
    # Requires a valid GITHUB_TOKEN in environment or .env
    owner = "streamlit"
    repo = "streamlit"

    # 1. Fetch repo info
    repo_info = get_repo_info(owner, repo)
    assert repo_info.stargazers_count > 0
    assert repo_info.forks_count > 0

    # 2. Fetch commits
    commits = get_commits(owner, repo)
    assert len(commits) > 0
    assert commits[0].name != ""

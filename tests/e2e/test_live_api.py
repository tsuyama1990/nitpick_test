import os

import pytest

from src.ingestion.github_client import GitHubClient


@pytest.mark.live
def test_live_api_repository_metadata() -> None:
    token = os.getenv("GITHUB_TOKEN")
    if not token or token == "dummy_token_for_tests":  # noqa: S105
        pytest.skip("No valid GITHUB_TOKEN provided for live tests.")

    client = GitHubClient(token=token)
    metadata = client.get_repository_metadata("torvalds", "linux")

    assert metadata.owner == "torvalds"
    assert metadata.repo == "linux"
    assert metadata.star_count > 0


@pytest.mark.live
def test_live_api_commits() -> None:
    token = os.getenv("GITHUB_TOKEN")
    if not token or token == "dummy_token_for_tests":  # noqa: S105
        pytest.skip("No valid GITHUB_TOKEN provided for live tests.")

    client = GitHubClient(token=token)
    commits = client.get_commits("torvalds", "linux")

    assert len(commits) > 0
    assert commits[0].commit_hash

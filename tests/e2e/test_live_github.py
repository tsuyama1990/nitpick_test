import os

import pytest
from src.ingestion.github_client import GithubClient

from src.config import get_config


@pytest.mark.live
def test_live_fetch_metadata() -> None:
    # This test will fail if run without GITHUB_TOKEN in env
    # Or we can just skip if not present
    token = os.getenv("GITHUB_TOKEN")
    if not token or token == "mock_token_for_tests":  # noqa: S105
        pytest.skip("No real GITHUB_TOKEN set for live tests")

    config = get_config()
    client = GithubClient(config)

    metadata = client.fetch_repository_metadata("torvalds", "linux")
    assert metadata.owner == "torvalds"
    assert metadata.name == "linux"
    assert metadata.stargazers_count > 10000


@pytest.mark.live
def test_live_fetch_commits() -> None:
    token = os.getenv("GITHUB_TOKEN")
    if not token or token == "mock_token_for_tests":  # noqa: S105
        pytest.skip("No real GITHUB_TOKEN set for live tests")

    config = get_config()
    client = GithubClient(config)

    commits = client.fetch_latest_commits("torvalds", "linux", limit=2)
    assert len(commits) == 2
    assert commits[0].sha

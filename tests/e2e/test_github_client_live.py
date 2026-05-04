import os

import pytest

from src.domain_models import CommitRecord, RepositoryMetadata
from src.ingestion.github_client import GitHubClient


@pytest.mark.live
def test_live_github_client_fetch() -> None:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        pytest.skip("GITHUB_TOKEN not configured in environment")

    client = GitHubClient(token=token)
    repo = client.get_repository_metadata("torvalds", "linux")
    assert isinstance(repo, RepositoryMetadata)
    assert repo.owner.lower() == "torvalds"
    assert repo.name.lower() == "linux"

    commits = client.get_recent_commits("torvalds", "linux")
    assert len(commits) > 0
    assert isinstance(commits[0], CommitRecord)

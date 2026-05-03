import os

import pytest

from src.config import Settings
from src.ingestion.github_client import GitHubClient


@pytest.mark.live
def test_live_repository_metadata_fetch() -> None:
    """
    Integration test skeleton.
    This test is intended to run against a live GitHub repository (like torvalds/linux)
    to ensure the API response matches our Pydantic schemas.
    It should be skipped in normal CI runs unless explicitly triggered.
    """
    # Check if a token is in the environment
    token = os.environ.get("GITHUB_TOKEN", "")
    mock_str = "mock_token"
    if not token or token == mock_str:
        pytest.skip("No valid GITHUB_TOKEN provided for live integration test.")

    settings = Settings()  # type: ignore[call-arg]
    client = GitHubClient(settings=settings)
    metadata = client.get_repository_metadata("torvalds", "linux")
    assert metadata.owner == "torvalds"
    assert metadata.repo_name == "linux"

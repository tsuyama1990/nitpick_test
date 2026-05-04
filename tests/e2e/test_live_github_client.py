import pytest

from src.config import get_settings
from src.domain_models import RepositoryMetadata
from src.ingestion.github_client import GitHubClient


@pytest.mark.live
def test_live_fetch_metadata() -> None:
    settings = get_settings()
    if not settings.github_token:
        pytest.skip("GITHUB_TOKEN not set, skipping live test.")

    client = GitHubClient(token=settings.github_token)
    meta = client.fetch_repository_metadata("streamlit/streamlit")

    assert isinstance(meta, RepositoryMetadata)
    assert meta.owner == "streamlit"
    assert meta.name == "streamlit"
    assert meta.stars > 0

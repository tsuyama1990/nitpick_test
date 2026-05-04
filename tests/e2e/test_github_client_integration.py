import pytest
from pytest_httpx import HTTPXMock

from src.domain_models.models import CommitRecord, RepositoryMetadata
from src.ingestion.github_client import GithubClient


def test_github_client_integration_mocked(
    httpx_mock: HTTPXMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "dummy_token")
    client = GithubClient()

    # Mocking metadata fetch
    httpx_mock.add_response(
        url="https://api.github.com/repos/streamlit/streamlit",
        json={
            "owner": {"login": "streamlit"},
            "name": "streamlit",
            "stargazers_count": 500,
            "forks_count": 50,
            "open_issues_count": 25,
        },
    )
    metadata = client.get_repository_metadata("streamlit", "streamlit")
    assert isinstance(metadata, RepositoryMetadata)

    # Mocking commits fetch
    httpx_mock.add_response(
        url="https://api.github.com/repos/streamlit/streamlit/commits?per_page=1",
        json=[
            {
                "sha": "xyz",
                "commit": {"author": {"name": "Test Author", "date": "2024-01-01T00:00:00Z"}},
            }
        ],
    )
    commits = client.get_recent_commits("streamlit", "streamlit", limit=1)
    assert len(commits) == 1
    assert isinstance(commits[0], CommitRecord)

@pytest.mark.live
def test_github_client_integration_live() -> None:
    client = GithubClient()
    metadata = client.get_repository_metadata("torvalds", "linux")
    assert isinstance(metadata, RepositoryMetadata)
    assert metadata.owner == "torvalds"
    assert metadata.repo == "linux"

    commits = client.get_recent_commits("torvalds", "linux", limit=2)
    assert len(commits) == 2
    assert isinstance(commits[0], CommitRecord)

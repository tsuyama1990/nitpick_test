import httpx
import pytest
import respx

from src.domain_models import (
    AuthenticationError,
    RateLimitError,
    RepositoryMetadata,
    RepositoryNotFoundError,
)
from src.ingestion.github_client import GitHubClient


@pytest.fixture
def mock_token_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "fake-token-123")


@respx.mock
def test_fetch_repository_metadata_success(mock_token_env: None) -> None:
    client = GitHubClient()

    mock_response = {
        "name": "streamlit",
        "owner": {"login": "streamlit"},
        "stargazers_count": 30000,
        "forks_count": 5000,
        "open_issues_count": 200,
    }

    respx.get("https://api.github.com/repos/streamlit/streamlit").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    repo = client.fetch_repository_metadata("streamlit", "streamlit")
    assert isinstance(repo, RepositoryMetadata)
    assert repo.name == "streamlit"
    assert repo.owner == "streamlit"
    assert repo.stargazers_count == 30000


@respx.mock
def test_fetch_repository_metadata_not_found(mock_token_env: None) -> None:
    client = GitHubClient()
    respx.get("https://api.github.com/repos/invalid/repo").mock(return_value=httpx.Response(404))

    with pytest.raises(RepositoryNotFoundError):
        client.fetch_repository_metadata("invalid", "repo")


@respx.mock
def test_fetch_repository_metadata_auth_error(mock_token_env: None) -> None:
    client = GitHubClient()
    respx.get("https://api.github.com/repos/streamlit/streamlit").mock(
        return_value=httpx.Response(401)
    )

    with pytest.raises(AuthenticationError):
        client.fetch_repository_metadata("streamlit", "streamlit")


@respx.mock
def test_fetch_repository_metadata_rate_limit(mock_token_env: None) -> None:
    client = GitHubClient()
    respx.get("https://api.github.com/repos/streamlit/streamlit").mock(
        return_value=httpx.Response(403, text="API Rate Limit Exceeded")
    )

    with pytest.raises(RateLimitError):
        client.fetch_repository_metadata("streamlit", "streamlit")


@respx.mock
def test_fetch_latest_commits_success(mock_token_env: None) -> None:
    client = GitHubClient()

    mock_response = [
        {
            "sha": "abc123def",
            "commit": {"author": {"name": "Test Author", "date": "2023-10-27T10:00:00Z"}},
        }
    ]

    respx.get("https://api.github.com/repos/streamlit/streamlit/commits?per_page=100").mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    commits = client.fetch_latest_commits("streamlit", "streamlit")
    assert len(commits) == 1
    assert commits[0].sha == "abc123def"
    assert commits[0].author_name == "Test Author"

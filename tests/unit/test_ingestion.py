import pytest
from pytest_httpx import HTTPXMock

from src.domain_models import RateLimitExceededError, RepositoryNotFoundError
from src.ingestion.github_client import GitHubClient


@pytest.fixture
def github_client() -> GitHubClient:
    return GitHubClient(token="test_token")


def test_github_client_initialization(github_client: GitHubClient) -> None:
    assert github_client.client.base_url == "https://api.github.com/"
    assert github_client.client.headers["Authorization"] == "Bearer test_token"
    assert github_client.client.headers["Accept"] == "application/vnd.github.v3+json"


def test_get_repository_metrics_success(github_client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test_owner/test_repo",
        json={"stargazers_count": 10, "forks_count": 5, "open_issues_count": 2},
    )
    result = github_client.get_repository_metrics("test_owner", "test_repo")
    assert result == {"stargazers_count": 10, "forks_count": 5, "open_issues_count": 2}


def test_get_repository_metrics_404(github_client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test_owner/test_repo", status_code=404
    )
    with pytest.raises(RepositoryNotFoundError):
        github_client.get_repository_metrics("test_owner", "test_repo")


def test_get_repository_metrics_403(github_client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test_owner/test_repo", status_code=403
    )
    with pytest.raises(RateLimitExceededError):
        github_client.get_repository_metrics("test_owner", "test_repo")


def test_get_repository_metrics_429(github_client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test_owner/test_repo", status_code=429
    )
    with pytest.raises(RateLimitExceededError):
        github_client.get_repository_metrics("test_owner", "test_repo")


def test_get_recent_commits_success(github_client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    mock_response = [{"commit": {"author": {"name": "Test", "date": "2024-01-01"}}}]
    httpx_mock.add_response(
        url="https://api.github.com/repos/test_owner/test_repo/commits?per_page=100",
        json=mock_response,
    )
    result = github_client.get_recent_commits("test_owner", "test_repo")
    assert result == mock_response


def test_get_recent_commits_404(github_client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test_owner/test_repo/commits?per_page=100",
        status_code=404,
    )
    with pytest.raises(RepositoryNotFoundError):
        github_client.get_recent_commits("test_owner", "test_repo")


def test_get_recent_commits_403(github_client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test_owner/test_repo/commits?per_page=100",
        status_code=403,
    )
    with pytest.raises(RateLimitExceededError):
        github_client.get_recent_commits("test_owner", "test_repo")


def test_get_recent_commits_429(github_client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test_owner/test_repo/commits?per_page=100",
        status_code=429,
    )
    with pytest.raises(RateLimitExceededError):
        github_client.get_recent_commits("test_owner", "test_repo")


@pytest.mark.skip(reason="Live API test")
def test_live_api_call() -> None:
    from src.domain_models.config import get_settings

    settings = get_settings()
    client = GitHubClient(token=settings.GITHUB_TOKEN)
    metrics = client.get_repository_metrics("streamlit", "streamlit")
    assert "stargazers_count" in metrics
    commits = client.get_recent_commits("streamlit", "streamlit", limit=5)
    assert len(commits) > 0

import pytest
from pytest_httpx import HTTPXMock

from src.domain.exceptions import RateLimitExceededError, RepositoryNotFoundError
from src.ingestion.github_client import GitHubClient


@pytest.fixture
def github_client() -> GitHubClient:
    return GitHubClient(token="dummy_test_token")  # noqa: S106


def test_github_client_headers(github_client: GitHubClient) -> None:
    assert github_client.client.headers["Authorization"] == "Bearer dummy_test_token"
    assert github_client.client.headers["Accept"] == "application/vnd.github.v3+json"
    assert github_client.client.base_url == "https://api.github.com/"


def test_get_repository_metrics_success(github_client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    mock_response = {
        "stargazers_count": 100,
        "forks_count": 50,
        "open_issues_count": 10,
    }
    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/repo",
        json=mock_response,
        status_code=200,
    )
    metrics = github_client.get_repository_metrics("owner", "repo")
    assert metrics == mock_response


def test_get_repository_metrics_not_found(
    github_client: GitHubClient, httpx_mock: HTTPXMock
) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/repo",
        status_code=404,
    )
    with pytest.raises(RepositoryNotFoundError):
        github_client.get_repository_metrics("owner", "repo")


def test_get_repository_metrics_rate_limit(
    github_client: GitHubClient, httpx_mock: HTTPXMock
) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/repo",
        status_code=403,
    )
    with pytest.raises(RateLimitExceededError):
        github_client.get_repository_metrics("owner", "repo")


def test_get_recent_commits_success(github_client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    mock_response = [{"sha": "abc"}, {"sha": "def"}]
    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/repo/commits?per_page=100",
        json=mock_response,
        status_code=200,
    )
    commits = github_client.get_recent_commits("owner", "repo", limit=100)
    assert commits == mock_response


def test_get_recent_commits_not_found(github_client: GitHubClient, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/repo/commits?per_page=100",
        status_code=404,
    )
    with pytest.raises(RepositoryNotFoundError):
        github_client.get_recent_commits("owner", "repo", limit=100)


@pytest.mark.skip(reason="Live API test")
def test_live_github_api() -> None:
    from src.config import get_settings

    settings = get_settings()
    client = GitHubClient(token=settings.GITHUB_TOKEN)
    metrics = client.get_repository_metrics("streamlit", "streamlit")
    assert "stargazers_count" in metrics

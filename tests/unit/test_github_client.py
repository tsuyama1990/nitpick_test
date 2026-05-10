
import pytest
from pytest_httpx import HTTPXMock

from src.config.settings import Settings
from src.domain_models.repository import RepoMetrics
from src.ingestion.github_client import GitHubAPIClient, GitHubAPIError


def test_fetch_repo_metrics_success(mock_settings: Settings, httpx_mock: HTTPXMock) -> None:
    client = GitHubAPIClient()
    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/repo",
        json={"stargazers_count": 100, "forks_count": 50, "open_issues_count": 10, "ignored_field": "test"}
    )

    metrics = client.fetch_repo_metrics("owner", "repo")

    assert isinstance(metrics, RepoMetrics)
    assert metrics.stars == 100
    assert metrics.forks == 50
    assert metrics.open_issues == 10

def test_fetch_recent_commits_success(mock_settings: Settings, httpx_mock: HTTPXMock) -> None:
    client = GitHubAPIClient()
    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/repo/commits?per_page=100",
        json=[
            {
                "commit": {
                    "author": {"name": "Alice", "date": "2023-10-01T12:00:00Z"}
                }
            },
            {
                "commit": {
                    "author": {"name": "Bob", "date": "2023-10-01T14:00:00Z"}
                }
            }
        ]
    )

    commits = client.fetch_recent_commits("owner", "repo")

    assert len(commits) == 2
    assert commits[0].author_name == "Alice"
    assert commits[1].author_name == "Bob"

def test_fetch_repo_metrics_404(mock_settings: Settings, httpx_mock: HTTPXMock) -> None:
    client = GitHubAPIClient()
    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/repo",
        status_code=404
    )

    with pytest.raises(GitHubAPIError, match="Repository not found"):
        client.fetch_repo_metrics("owner", "repo")

def test_fetch_repo_metrics_403(mock_settings: Settings, httpx_mock: HTTPXMock) -> None:
    client = GitHubAPIClient()
    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/repo",
        status_code=403
    )

    with pytest.raises(GitHubAPIError, match="Rate limit exceeded"):
        client.fetch_repo_metrics("owner", "repo")


import pytest
from pytest_httpx import HTTPXMock

from src.ingestion.client import GitHubClient, GitHubClientError


@pytest.fixture
def mock_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "fake_token")

def test_get_repository_info_success(mock_settings: None, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test/test-repo",
        json={"stargazers_count": 10, "forks_count": 5, "open_issues_count": 2}
    )
    client = GitHubClient()
    repo = client.get_repository_info("test", "test-repo")
    assert repo.stargazers_count == 10
    assert repo.forks_count == 5

def test_get_repository_info_404(mock_settings: None, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test/test-repo",
        status_code=404
    )
    client = GitHubClient()
    with pytest.raises(GitHubClientError, match="HTTP 404 Not Found"):
        client.get_repository_info("test", "test-repo")

def test_get_repository_info_403(mock_settings: None, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test/test-repo",
        status_code=403
    )
    client = GitHubClient()
    with pytest.raises(GitHubClientError, match="HTTP 403 Forbidden"):
        client.get_repository_info("test", "test-repo")

def test_get_repository_info_429(mock_settings: None, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test/test-repo",
        status_code=429
    )
    client = GitHubClient()
    with pytest.raises(GitHubClientError, match="HTTP 429 Too Many Requests"):
        client.get_repository_info("test", "test-repo")

def test_get_recent_commits_success(mock_settings: None, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test/test-repo/commits?per_page=100",
        json=[
            {
                "sha": "abc1234",
                "commit": {
                    "committer": {
                        "name": "Alice",
                        "date": "2023-01-01T12:00:00Z"
                    }
                }
            }
        ]
    )
    client = GitHubClient()
    commits = client.get_recent_commits("test", "test-repo")
    assert len(commits) == 1
    assert commits[0].sha == "abc1234"
    assert commits[0].commit.committer.name == "Alice"

def test_get_repository_info_type_error(mock_settings: None, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test/test-repo",
        json=["not", "a", "dict"]
    )
    client = GitHubClient()
    with pytest.raises(TypeError, match="Response is not a dictionary"):
        client.get_repository_info("test", "test-repo")

def test_get_recent_commits_type_error(mock_settings: None, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.github.com/repos/test/test-repo/commits?per_page=100",
        json={"not": "a list"}
    )
    client = GitHubClient()
    with pytest.raises(TypeError, match="Response is not a list"):
        client.get_recent_commits("test", "test-repo")

@pytest.mark.live
def test_live_github_api() -> None:
    import os
    if "GITHUB_TOKEN" not in os.environ:
        pytest.skip("GITHUB_TOKEN not set")

    client = GitHubClient()
    repo = client.get_repository_info("streamlit", "streamlit")
    assert repo.stargazers_count > 0

def test_network_error(mock_settings: None, httpx_mock: HTTPXMock) -> None:
    from httpx import RequestError
    httpx_mock.add_exception(RequestError("Mocked network error"))
    client = GitHubClient()
    with pytest.raises(GitHubClientError, match="Network error during request"):
        client.get_repository_info("test", "test-repo")

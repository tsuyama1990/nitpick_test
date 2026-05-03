import datetime

import pytest
import respx
from httpx import Response

from src.config import Settings
from src.domain_models.exceptions import (
    AuthenticationError,
    RateLimitError,
    RepositoryNotFoundError,
)
from src.domain_models.models import CommitRecord, RepositoryMetadata
from src.ingestion.github_client import GitHubClient


@pytest.fixture
def mock_settings(monkeypatch: pytest.MonkeyPatch) -> Settings:
    monkeypatch.setenv("GITHUB_TOKEN", "mock_token")
    return Settings()  # type: ignore[call-arg]


@pytest.fixture
def client(mock_settings: Settings) -> GitHubClient:
    return GitHubClient(settings=mock_settings)


@respx.mock
def test_fetch_metadata_success(client: GitHubClient) -> None:
    repo_owner = "test-owner"
    repo_name = "test-repo"

    mock_response = {
        "name": repo_name,
        "owner": {"login": repo_owner},
        "stargazers_count": 100,
        "forks_count": 50,
        "open_issues_count": 10,
    }

    respx.get(f"https://api.github.com/repos/{repo_owner}/{repo_name}").mock(
        return_value=Response(200, json=mock_response)
    )

    metadata = client.get_repository_metadata(repo_owner, repo_name)

    assert isinstance(metadata, RepositoryMetadata)
    assert metadata.owner == repo_owner
    assert metadata.repo_name == repo_name
    assert metadata.star_count == 100
    assert metadata.fork_count == 50
    assert metadata.open_issue_count == 10


@respx.mock
def test_fetch_commits_success(client: GitHubClient) -> None:
    repo_owner = "test-owner"
    repo_name = "test-repo"

    mock_response = [
        {
            "sha": "abcdef123456",
            "commit": {
                "author": {"name": "Test Author", "date": "2023-10-27T10:00:00Z"}
            },
        }
    ]

    respx.get(
        f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits?per_page=100"
    ).mock(return_value=Response(200, json=mock_response))

    commits = client.get_recent_commits(repo_owner, repo_name)

    assert isinstance(commits, list)
    assert len(commits) == 1
    assert isinstance(commits[0], CommitRecord)
    assert commits[0].commit_hash == "abcdef123456"
    assert commits[0].author_name == "Test Author"
    assert (
        commits[0].timestamp
        == datetime.datetime(2023, 10, 27, 10, 0, 0, tzinfo=datetime.UTC)
    )


@respx.mock
def test_not_found_error(client: GitHubClient) -> None:
    repo_owner = "test-owner"
    repo_name = "invalid-repo"

    respx.get(f"https://api.github.com/repos/{repo_owner}/{repo_name}").mock(
        return_value=Response(404, json={"message": "Not Found"})
    )

    with pytest.raises(RepositoryNotFoundError):
        client.get_repository_metadata(repo_owner, repo_name)


@respx.mock
def test_authentication_error(client: GitHubClient) -> None:
    repo_owner = "test-owner"
    repo_name = "test-repo"

    respx.get(f"https://api.github.com/repos/{repo_owner}/{repo_name}").mock(
        return_value=Response(401, json={"message": "Bad credentials"})
    )

    with pytest.raises(AuthenticationError) as exc_info:
        client.get_repository_metadata(repo_owner, repo_name)

    assert "mock_token" not in str(exc_info.value)


@respx.mock
def test_rate_limit_error(client: GitHubClient) -> None:
    repo_owner = "test-owner"
    repo_name = "test-repo"

    respx.get(f"https://api.github.com/repos/{repo_owner}/{repo_name}").mock(
        return_value=Response(403, json={"message": "API rate limit exceeded"})
    )

    with pytest.raises(RateLimitError):
        client.get_repository_metadata(repo_owner, repo_name)

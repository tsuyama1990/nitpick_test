import pytest
from httpx import Response
from pytest_mock import MockerFixture

from src.domain.exceptions import (
    AuthenticationError,
    RateLimitError,
    RepositoryNotFoundError,
)
from src.domain.models import CommitRecord, RepositoryMetadata
from src.ingestion.github_client import GitHubClient


def test_fetch_repository_metadata_success(mocker: MockerFixture) -> None:
    mock_get = mocker.patch("httpx.Client.get")
    mock_get.return_value = Response(
        200,
        json={
            "name": "streamlit",
            "owner": {"login": "streamlit"},
            "stargazers_count": 30000,
            "forks_count": 2000,
            "open_issues_count": 150
        }
    )

    client = GitHubClient(token="fake_token")
    repo = client.fetch_repository_metadata("streamlit/streamlit")

    assert isinstance(repo, RepositoryMetadata)
    assert repo.name == "streamlit"
    assert repo.owner == "streamlit"
    assert repo.stargazers_count == 30000

def test_fetch_repository_metadata_not_found(mocker: MockerFixture) -> None:
    mock_get = mocker.patch("httpx.Client.get")
    mock_get.return_value = Response(404, json={})

    client = GitHubClient(token="fake_token")
    with pytest.raises(RepositoryNotFoundError):
        client.fetch_repository_metadata("invalid/repo")

def test_fetch_repository_metadata_auth_error(mocker: MockerFixture) -> None:
    mock_get = mocker.patch("httpx.Client.get")
    mock_get.return_value = Response(401, json={})

    client = GitHubClient(token="fake_token")
    with pytest.raises(AuthenticationError) as exc_info:
        client.fetch_repository_metadata("streamlit/streamlit")

    # Ensure token is not leaked
    assert "fake_token" not in str(exc_info.value)

def test_fetch_repository_metadata_rate_limit(mocker: MockerFixture) -> None:
    mock_get = mocker.patch("httpx.Client.get")
    mock_get.return_value = Response(429, json={})

    client = GitHubClient(token="fake_token")
    with pytest.raises(RateLimitError):
        client.fetch_repository_metadata("streamlit/streamlit")

def test_fetch_commits_success(mocker: MockerFixture) -> None:
    mock_get = mocker.patch("httpx.Client.get")
    mock_get.return_value = Response(
        200,
        json=[
            {
                "sha": "12345",
                "commit": {
                    "author": {"name": "Test User", "date": "2023-01-01T10:00:00Z"}
                }
            }
        ]
    )

    client = GitHubClient(token="fake_token")
    commits = client.fetch_commits("streamlit/streamlit", limit=1)

    assert len(commits) == 1
    assert isinstance(commits[0], CommitRecord)
    assert commits[0].sha == "12345"
    assert commits[0].author_name == "Test User"

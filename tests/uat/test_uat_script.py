import pytest
from httpx import Response
from pytest_mock import MockerFixture

from src.domain.exceptions import AuthenticationError, RepositoryNotFoundError
from src.domain.models import RepositoryMetadata
from src.ingestion.github_client import GitHubClient


def test_uat_c01_01_successful_data_extraction(mocker: MockerFixture) -> None:
    # Given a valid token and client
    mock_get = mocker.patch("httpx.Client.get")
    mock_get.side_effect = [
        Response(200, json={
            "name": "streamlit",
            "owner": {"login": "streamlit"},
            "stargazers_count": 30000,
            "forks_count": 2000,
            "open_issues_count": 150
        }),
        Response(200, json=[
            {
                "sha": "123",
                "commit": {"author": {"name": "User", "date": "2023-01-01T10:00:00Z"}}
            }
        ])
    ]

    client = GitHubClient(token="valid_token")

    # When requesting metadata and commits
    repo = client.fetch_repository_metadata("streamlit/streamlit")
    commits = client.fetch_commits("streamlit/streamlit", limit=1)

    # Then returns valid strictly typed models
    assert isinstance(repo, RepositoryMetadata)
    assert len(commits) == 1

def test_uat_c01_02_error_handling_invalid_repos(mocker: MockerFixture) -> None:
    # Given an invalid repo string
    mock_get = mocker.patch("httpx.Client.get")
    mock_get.return_value = Response(404, json={})

    client = GitHubClient(token="valid_token")

    # When fetching
    # Then it raises RepositoryNotFoundError
    with pytest.raises(RepositoryNotFoundError):
        client.fetch_repository_metadata("invalid-owner/non-existent-repo")

def test_uat_c01_03_authentication_failure(mocker: MockerFixture) -> None:
    # Given an invalid token
    mock_get = mocker.patch("httpx.Client.get")
    mock_get.return_value = Response(401, json={})

    client = GitHubClient(token="invalid_token_123")

    # When fetching
    # Then it raises AuthenticationError securely
    with pytest.raises(AuthenticationError) as exc_info:
        client.fetch_repository_metadata("streamlit/streamlit")

    assert "invalid_token_123" not in str(exc_info.value)

import pytest
from httpx import Response
from pytest_mock import MockerFixture

from src.domain_models.exceptions import (
    AuthenticationError,
    RateLimitError,
    RepositoryNotFoundError,
)
from src.ingestion.github_client import GithubClient


@pytest.fixture
def client() -> GithubClient:
    return GithubClient(token="dummy_token")  # noqa: S106


def test_fetch_repository_metadata_success(client: GithubClient, mocker: MockerFixture) -> None:
    mock_response = Response(
        200,
        json={
            "owner": {"login": "streamlit"},
            "name": "streamlit",
            "stargazers_count": 100,
            "forks_count": 50,
            "open_issues_count": 10,
        },
    )
    mocker.patch("httpx.Client.get", return_value=mock_response)

    repo = client.fetch_repository_metadata("streamlit/streamlit")

    assert repo.owner == "streamlit"
    assert repo.name == "streamlit"
    assert repo.star_count == 100
    assert repo.fork_count == 50
    assert repo.open_issue_count == 10


def test_fetch_commits_success(client: GithubClient, mocker: MockerFixture) -> None:
    mock_response = Response(
        200,
        json=[
            {
                "sha": "abcdef",
                "commit": {"author": {"name": "John Doe", "date": "2023-01-01T00:00:00Z"}},
            }
        ],
    )
    mocker.patch("httpx.Client.get", return_value=mock_response)

    commits = client.fetch_commits("streamlit/streamlit")

    assert len(commits) == 1
    assert commits[0].sha == "abcdef"
    assert commits[0].author_name == "John Doe"


def test_fetch_repository_metadata_404(client: GithubClient, mocker: MockerFixture) -> None:
    mock_response = Response(404)
    mocker.patch("httpx.Client.get", return_value=mock_response)

    with pytest.raises(RepositoryNotFoundError):
        client.fetch_repository_metadata("streamlit/invalid_repo")


def test_fetch_repository_metadata_401(client: GithubClient, mocker: MockerFixture) -> None:
    mock_response = Response(401)
    mocker.patch("httpx.Client.get", return_value=mock_response)

    with pytest.raises(AuthenticationError):
        client.fetch_repository_metadata("streamlit/streamlit")


def test_fetch_repository_metadata_403(client: GithubClient, mocker: MockerFixture) -> None:
    mock_response = Response(403)
    mocker.patch("httpx.Client.get", return_value=mock_response)

    with pytest.raises(AuthenticationError):
        client.fetch_repository_metadata("streamlit/streamlit")


def test_fetch_repository_metadata_429(client: GithubClient, mocker: MockerFixture) -> None:
    mock_response = Response(429)
    mocker.patch("httpx.Client.get", return_value=mock_response)

    with pytest.raises(RateLimitError):
        client.fetch_repository_metadata("streamlit/streamlit")


def test_client_initialization_without_token() -> None:
    with pytest.raises(ValueError, match="GitHub token cannot be empty"):
        GithubClient(token="")

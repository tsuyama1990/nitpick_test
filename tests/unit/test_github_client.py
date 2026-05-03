import pytest
from httpx import HTTPStatusError, RequestError, Response
from pytest_mock import MockerFixture

from src.domain_models import (
    APIConnectionError,
    AuthenticationError,
    CommitRecord,
    RateLimitError,
    RepositoryMetadata,
    RepositoryNotFoundError,
)
from src.ingestion.github_client import GitHubClient


@pytest.fixture
def client() -> GitHubClient:
    token_str = "test_token"  # noqa: S105
    return GitHubClient(token=token_str)


def test_get_repository_metadata_success(client: GitHubClient, mocker: MockerFixture) -> None:
    mock_response = mocker.Mock(spec=Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "owner": {"login": "streamlit"},
        "name": "streamlit",
        "stargazers_count": 1000,
        "forks_count": 200,
        "open_issues_count": 50,
    }
    mock_response.raise_for_status.return_value = None

    mock_get = mocker.patch("httpx.Client.get", return_value=mock_response)

    result = client.get_repository_metadata("streamlit", "streamlit")

    mock_get.assert_called_once_with("https://api.github.com/repos/streamlit/streamlit")
    assert isinstance(result, RepositoryMetadata)
    assert result.owner == "streamlit"
    assert result.stars == 1000


def test_get_recent_commits_success(client: GitHubClient, mocker: MockerFixture) -> None:
    mock_response = mocker.Mock(spec=Response)
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"sha": "abc", "commit": {"author": {"name": "John", "date": "2023-01-01T12:00:00Z"}}}
    ]
    mock_response.raise_for_status.return_value = None

    mock_get = mocker.patch("httpx.Client.get", return_value=mock_response)

    result = client.get_recent_commits("streamlit", "streamlit")

    mock_get.assert_called_once_with(
        "https://api.github.com/repos/streamlit/streamlit/commits", params={"per_page": 100}
    )
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], CommitRecord)
    assert result[0].commit_hash == "abc"


def test_get_repository_metadata_404(client: GitHubClient, mocker: MockerFixture) -> None:
    mock_response = mocker.Mock(spec=Response)
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = HTTPStatusError(
        "404 Not Found", request=mocker.Mock(), response=mock_response
    )

    mocker.patch("httpx.Client.get", return_value=mock_response)

    with pytest.raises(RepositoryNotFoundError):
        client.get_repository_metadata("streamlit", "streamlit")


def test_get_repository_metadata_401(client: GitHubClient, mocker: MockerFixture) -> None:
    mock_response = mocker.Mock(spec=Response)
    mock_response.status_code = 401
    mock_response.raise_for_status.side_effect = HTTPStatusError(
        "401 Unauthorized", request=mocker.Mock(), response=mock_response
    )

    mocker.patch("httpx.Client.get", return_value=mock_response)

    with pytest.raises(AuthenticationError):
        client.get_repository_metadata("streamlit", "streamlit")


def test_get_repository_metadata_403_rate_limit(
    client: GitHubClient, mocker: MockerFixture
) -> None:
    mock_response = mocker.Mock(spec=Response)
    mock_response.status_code = 403
    mock_response.raise_for_status.side_effect = HTTPStatusError(
        "403 Forbidden", request=mocker.Mock(), response=mock_response
    )

    mocker.patch("httpx.Client.get", return_value=mock_response)

    with pytest.raises(RateLimitError):
        client.get_repository_metadata("streamlit", "streamlit")


def test_get_repository_metadata_429(client: GitHubClient, mocker: MockerFixture) -> None:
    mock_response = mocker.Mock(spec=Response)
    mock_response.status_code = 429
    mock_response.raise_for_status.side_effect = HTTPStatusError(
        "429 Too Many Requests", request=mocker.Mock(), response=mock_response
    )

    mocker.patch("httpx.Client.get", return_value=mock_response)

    with pytest.raises(RateLimitError):
        client.get_repository_metadata("streamlit", "streamlit")


def test_get_repository_metadata_connection_error(
    client: GitHubClient, mocker: MockerFixture
) -> None:
    mocker.patch(
        "httpx.Client.get", side_effect=RequestError("Connection Refused", request=mocker.Mock())
    )

    with pytest.raises(APIConnectionError):
        client.get_repository_metadata("streamlit", "streamlit")

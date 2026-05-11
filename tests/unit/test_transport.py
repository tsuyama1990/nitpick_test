import httpx
import pytest
from pytest_mock import MockerFixture

from src.ingestion.github_client import GitHubClient


def test_github_client_transport_error(mocker: MockerFixture) -> None:
    mock_response = mocker.Mock(spec=httpx.Response)
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = httpx.HTTPError("Transport failed")

    mocker.patch("httpx.Client.get", return_value=mock_response)

    with (
        GitHubClient(token="mock") as client,  # noqa: S106
        pytest.raises(httpx.HTTPError, match="Transport Error:"),
    ):
        client.get_repository_metrics("owner", "repo")

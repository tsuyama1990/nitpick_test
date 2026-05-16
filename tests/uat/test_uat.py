import pytest
from pytest_httpx import HTTPXMock

from src.domain_models.config import Settings
from src.domain_models.exceptions import RepositoryNotFoundError
from src.domain_models.schemas import RepositoryMetrics
from src.ingestion.github_client import GitHubClient


def test_uat_c02_01_successful_data_retrieval(httpx_mock: HTTPXMock) -> None:
    """
    UAT-C02-01: Successful Data Retrieval
    GIVEN the GitHub API Client is configured with a valid token
    AND the network layer is mocked to return a valid JSON payload for the `streamlit/streamlit` repository
    WHEN a request is made to fetch repository metrics
    THEN the client must return a Python dictionary containing the expected keys
         (`stargazers_count`, `forks_count`, `open_issues_count`) corresponding to the mock data.
    """
    # GIVEN
    settings = Settings(GITHUB_TOKEN="valid_mock_token")  # noqa: S106
    mock_payload = {
        "stargazers_count": 30000,
        "forks_count": 3000,
        "open_issues_count": 500,
        "other_field": "should be dropped as per model config",
    }
    httpx_mock.add_response(
        url="https://api.github.com/repos/streamlit/streamlit",
        json=mock_payload,
        status_code=200,
    )

    # WHEN
    with GitHubClient(settings=settings) as client:
        result = client.get_repository_metrics("streamlit", "streamlit")

    # THEN
    assert isinstance(result, RepositoryMetrics)
    assert result.stargazers_count == 30000
    assert result.forks_count == 3000
    assert result.open_issues_count == 500


def test_uat_c02_02_graceful_error_translation(httpx_mock: HTTPXMock) -> None:
    """
    UAT-C02-02: Graceful Error Translation
    GIVEN the network layer is mocked to return an HTTP 404 Not Found status code
    WHEN a request is made to fetch metrics for a non-existent repository (e.g., `invalid-owner/invalid-repo`)
    THEN the client must intercept the HTTP error
    AND explicitly raise a `RepositoryNotFoundError` to prevent raw HTTP traces from propagating up the application stack.
    """
    # GIVEN
    settings = Settings(GITHUB_TOKEN="valid_mock_token")  # noqa: S106
    httpx_mock.add_response(
        url="https://api.github.com/repos/invalid-owner/invalid-repo",
        status_code=404,
    )

    # WHEN / THEN
    with (
        GitHubClient(settings=settings) as client,
        pytest.raises(
            RepositoryNotFoundError, match="Repository invalid-owner/invalid-repo not found"
        ),
    ):
        client.get_repository_metrics("invalid-owner", "invalid-repo")

from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest

from src.domain_models.commit import CommitData
from src.domain_models.repository import RepositoryInfo
from src.services.github import fetch_repository_data


@pytest.fixture
def mock_httpx_client() -> Generator[MagicMock, None, None]:
    with patch("httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value.__enter__.return_value = mock_client
        yield mock_client


def test_fetch_repository_data_success(mock_httpx_client: MagicMock) -> None:
    mock_repo_resp = MagicMock()
    mock_repo_resp.status_code = 200
    mock_repo_resp.json.return_value = {
        "name": "streamlit",
        "owner": {"login": "streamlit"},
        "stargazers_count": 1000,
        "forks_count": 200,
        "open_issues_count": 10,
    }

    mock_commits_resp = MagicMock()
    mock_commits_resp.status_code = 200
    mock_commits_resp.json.return_value = [
        {
            "sha": "abcdef123456",
            "commit": {
                "author": {"name": "John Doe", "date": "2023-10-01T12:00:00Z"},
                "message": "Initial commit",
            },
        }
    ]

    mock_httpx_client.get.side_effect = [mock_repo_resp, mock_commits_resp]

    repo_info, commits = fetch_repository_data("fake_token", "streamlit", "streamlit")

    assert isinstance(repo_info, RepositoryInfo)
    assert repo_info.name == "streamlit"
    assert repo_info.stargazers_count == 1000

    assert len(commits) == 1
    assert isinstance(commits[0], CommitData)
    assert commits[0].sha == "abcdef123456"


def test_fetch_repository_data_not_found(mock_httpx_client: MagicMock) -> None:
    mock_repo_resp = MagicMock()
    mock_repo_resp.status_code = 404

    mock_httpx_client.get.return_value = mock_repo_resp

    with pytest.raises(ValueError, match="not found"):
        fetch_repository_data("fake_token", "invalid", "repo")

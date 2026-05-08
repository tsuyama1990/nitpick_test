import pytest
from pytest_httpx import HTTPXMock

from src.ingestion.github_client import get_commits, get_repo_info


@pytest.fixture
def mock_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "fake_token")

def test_get_repo_info_success(httpx_mock: HTTPXMock, mock_env: None) -> None:
    httpx_mock.add_response(json={"stargazers_count": 10, "forks_count": 5, "open_issues_count": 2})

    info = get_repo_info("owner", "repo")
    assert info.stargazers_count == 10
    assert info.forks_count == 5

def test_get_repo_info_403(httpx_mock: HTTPXMock, mock_env: None) -> None:
    httpx_mock.add_response(status_code=403, json={"message": "Forbidden"})
    with pytest.raises(RuntimeError, match="403 Forbidden"):
        get_repo_info("owner", "repo")

def test_get_commits_success(httpx_mock: HTTPXMock, mock_env: None) -> None:
    httpx_mock.add_response(json=[
        {"commit": {"author": {"name": "User1", "date": "2023-10-27T10:00:00Z"}}},
        {"commit": {"author": {"name": "User2", "date": "2023-10-27T11:00:00Z"}}}
    ])

    commits = get_commits("owner", "repo")
    assert len(commits) == 2
    assert commits[0].name == "User1"

import pathlib
from collections.abc import Generator
from unittest.mock import patch

import polars as pl
import pytest
from pytest_httpx import HTTPXMock

from src.clients.github_client import GitHubClient, GitHubClientError
from src.domain_models.config import Settings
from src.services.data_processor import DataProcessor


@pytest.fixture
def mock_settings(tmp_path: pathlib.Path) -> Generator[Settings, None, None]:
    settings = Settings(GITHUB_TOKEN="test_token", CACHE_DIR=tmp_path)  # noqa: S106
    with (
        patch("src.clients.github_client.get_settings", return_value=settings),
        patch("src.services.data_processor.get_settings", return_value=settings),
    ):
        yield settings


def test_github_client_repo_info(httpx_mock: HTTPXMock, mock_settings: Settings) -> None:
    client = GitHubClient()
    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/repo",
        json={"stargazers_count": 10, "forks_count": 5, "open_issues_count": 2, "extra": "ignore"},
    )
    repo = client.get_repo_info("owner", "repo")
    assert repo.stargazers_count == 10
    assert repo.forks_count == 5
    assert repo.open_issues_count == 2


def test_github_client_commits(httpx_mock: HTTPXMock, mock_settings: Settings) -> None:
    client = GitHubClient()
    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/repo/commits?per_page=100",
        json=[
            {
                "sha": "123",
                "commit": {"author": {"name": "Alice", "date": "2023-01-01T00:00:00Z"}},
                "extra": "ignore",
            }
        ],
    )
    commits = client.get_commits("owner", "repo")
    assert len(commits) == 1
    assert commits[0].sha == "123"
    assert commits[0].author_name == "Alice"
    assert commits[0].date == "2023-01-01T00:00:00Z"


def test_github_client_403_error(httpx_mock: HTTPXMock, mock_settings: Settings) -> None:
    client = GitHubClient()
    httpx_mock.add_response(url="https://api.github.com/repos/owner/repo", status_code=403)
    with pytest.raises(GitHubClientError, match="Rate limit exceeded"):
        client.get_repo_info("owner", "repo")


def test_github_client_404_error(httpx_mock: HTTPXMock, mock_settings: Settings) -> None:
    client = GitHubClient()
    httpx_mock.add_response(url="https://api.github.com/repos/owner/repo", status_code=404)
    with pytest.raises(GitHubClientError, match="Repository not found"):
        client.get_repo_info("owner", "repo")


def test_data_processor_aggregate_commits_by_date(mock_settings: Settings) -> None:
    processor = DataProcessor()
    df = pl.DataFrame(
        [
            {"sha": "1", "author_name": "A", "date": "2023-01-01T10:00:00Z"},
            {"sha": "2", "author_name": "B", "date": "2023-01-01T11:00:00Z"},
            {"sha": "3", "author_name": "A", "date": "2023-01-02T10:00:00Z"},
        ]
    )
    result = processor._aggregate_commits_by_date(df)

    expected = pl.DataFrame(
        {"date_only": ["2023-01-01", "2023-01-02"], "commit_count": [2, 1]},
        schema={"date_only": pl.Date, "commit_count": pl.UInt32},
    )
    assert result.equals(expected)


def test_data_processor_aggregate_top_committers(mock_settings: Settings) -> None:
    processor = DataProcessor()
    df = pl.DataFrame(
        [
            {"sha": "1", "author_name": "Alice", "date": "2023-01-01"},
            {"sha": "2", "author_name": "Alice", "date": "2023-01-01"},
            {"sha": "3", "author_name": "Bob", "date": "2023-01-01"},
            {"sha": "4", "author_name": "Charlie", "date": "2023-01-01"},
            {"sha": "5", "author_name": "Dave", "date": "2023-01-01"},
            {"sha": "6", "author_name": "Eve", "date": "2023-01-01"},
            {"sha": "7", "author_name": "Frank", "date": "2023-01-01"},
        ]
    )
    result = processor._aggregate_top_committers(df)

    assert len(result) == 5
    assert result["author_name"][0] == "Alice"
    assert result["commit_count"][0] == 2


def test_data_processor_cache_repo(httpx_mock: HTTPXMock, mock_settings: Settings) -> None:
    processor = DataProcessor()
    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/repo",
        json={"stargazers_count": 10, "forks_count": 5, "open_issues_count": 2},
    )
    # First call fetches from API
    repo1 = processor.get_repo_data("owner", "repo")
    assert repo1.stargazers_count == 10

    # Clear mocks to ensure no network calls on second attempt
    httpx_mock.reset()

    # Second call fetches from cache
    repo2 = processor.get_repo_data("owner", "repo")
    assert repo2.stargazers_count == 10


def test_data_processor_cache_commits(httpx_mock: HTTPXMock, mock_settings: Settings) -> None:
    processor = DataProcessor()
    httpx_mock.add_response(
        url="https://api.github.com/repos/owner/repo/commits?per_page=100",
        json=[
            {"sha": "123", "commit": {"author": {"name": "Alice", "date": "2023-01-01T00:00:00Z"}}}
        ],
    )
    # First call fetches from API
    df_date1, df_user1 = processor.get_commit_data("owner", "repo")
    assert len(df_date1) == 1

    httpx_mock.reset()

    # Second call fetches from cache
    df_date2, df_user2 = processor.get_commit_data("owner", "repo")
    assert len(df_date2) == 1

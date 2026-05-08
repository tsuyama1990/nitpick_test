from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from src.domain_models.github import CommitDetail, RepositoryInfo


def test_repository_info_valid() -> None:
    data: dict[str, object] = {
        "full_name": "owner/repo",
        "stargazers_count": 100,
        "forks_count": 50,
        "open_issues_count": 10,
        "extra_field": "ignore_me",
    }
    repo_info = RepositoryInfo(**data)  # type: ignore[arg-type]
    assert repo_info.name == "owner/repo"
    assert repo_info.stars == 100
    assert repo_info.forks == 50
    assert repo_info.open_issues == 10


def test_repository_info_invalid() -> None:
    data: dict[str, object] = {
        "full_name": "owner/repo",
        "stargazers_count": "not_an_int",
        "forks_count": 50,
        "open_issues_count": 10,
    }
    with pytest.raises(ValidationError):
        RepositoryInfo(**data)  # type: ignore[arg-type]


def test_commit_detail_valid() -> None:
    data: dict[str, object] = {
        "sha": "1234567890abcdef",
        "commit": {
            "author": {
                "name": "Test User",
                "date": "2023-01-01T12:00:00Z",
            },
            "message": "Initial commit",
        },
        "extra_field": "ignore_me",
    }
    commit = CommitDetail(**data)  # type: ignore[arg-type]
    assert commit.sha == "1234567890abcdef"
    assert commit.message == "Initial commit"
    assert commit.author_name == "Test User"
    assert commit.author_date == datetime(2023, 1, 1, 12, 0, tzinfo=UTC)


def test_commit_detail_invalid() -> None:
    data: dict[str, object] = {
        "sha": "1234567890abcdef",
        "commit": {
            "author": {
                "name": "Test User",
                "date": "invalid_date",
            },
            "message": "Initial commit",
        },
    }
    with pytest.raises(ValidationError):
        CommitDetail(**data)  # type: ignore[arg-type]

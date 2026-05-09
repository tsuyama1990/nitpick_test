from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from src.domain_models.config import Settings
from src.domain_models.github import GitHubCommit, GitHubRepository, StrictBaseModel


def test_settings_forbid_extra() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Settings(GITHUB_TOKEN="test_token", UNKNOWN_VARIABLE="test")  # type: ignore[call-arg]  # noqa: S106

    # Check if any error is of type 'extra_forbidden'
    assert any(err["type"] == "extra_forbidden" for err in exc_info.value.errors())


def test_strict_base_model_invalid_type() -> None:
    data = "not a dict"
    with pytest.raises(TypeError):
        StrictBaseModel._strip_extra(data)

    with pytest.raises(TypeError):
        GitHubRepository(**data)  # type: ignore[arg-type]


def test_github_repository_valid() -> None:
    data: dict[str, Any] = {
        "owner": {"login": "streamlit", "id": 123},
        "name": "streamlit",
        "stargazers_count": 100,
        "forks_count": 50,
        "open_issues_count": 10,
        "unknown_field": "ignore_me",
    }
    repo = GitHubRepository(**data)
    assert repo.owner == "streamlit"
    assert repo.name == "streamlit"
    assert repo.stargazers_count == 100


def test_github_repository_invalid_metrics() -> None:
    data: dict[str, Any] = {
        "owner": "streamlit",
        "name": "streamlit",
        "stargazers_count": -1,
        "forks_count": 50,
        "open_issues_count": 10,
    }
    with pytest.raises(ValidationError):
        GitHubRepository(**data)


def test_github_commit_valid() -> None:
    data: dict[str, Any] = {
        "sha": "1234567890abcdef",
        "commit": {
            "author": {
                "name": "Test User",
                "email": "test@example.com",
                "date": "2023-01-01T12:00:00Z",
            },
            "message": "Test commit message",
            "unknown_commit_field": "ignore_me",
        },
        "unknown_root_field": "ignore_me",
    }
    commit = GitHubCommit(**data)
    assert commit.sha == "1234567890abcdef"
    assert commit.commit.message == "Test commit message"
    assert commit.commit.author.name == "Test User"
    assert commit.commit.author.date == datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC)


def test_github_commit_invalid_author_type() -> None:
    data = "invalid_data"
    with pytest.raises(TypeError):
        GitHubCommit(**data)  # type: ignore[arg-type]


def test_github_repository_owner_string() -> None:
    data: dict[str, Any] = {
        "owner": "justastring",
        "name": "streamlit",
        "stargazers_count": 100,
        "forks_count": 50,
        "open_issues_count": 10,
    }
    repo = GitHubRepository(**data)
    assert repo.owner == "justastring"

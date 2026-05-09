from typing import Any

import pytest
from pydantic import ValidationError

from src.domain_models import Commit, Repository, Settings


def test_settings_forbids_extra_fields() -> None:
    """Settings should reject unknown variables when extra='forbid' is used."""
    with pytest.raises(ValidationError):
        Settings(GITHUB_TOKEN="dummy_token", UNKNOWN_VARIABLE="test")  # type: ignore[call-arg]


def test_repository_model_valid() -> None:
    """Repository model should parse valid data correctly."""
    data: dict[str, Any] = {
        "id": 123,
        "name": "test-repo",
        "full_name": "owner/test-repo",
        "stargazers_count": 10,
        "forks_count": 5,
        "open_issues_count": 2,
    }
    repo = Repository(**data)
    assert repo.id == 123
    assert repo.name == "test-repo"
    assert repo.stargazers_count == 10


def test_repository_model_forbids_extra() -> None:
    """Repository model should reject extra fields natively."""
    data: dict[str, Any] = {
        "id": 123,
        "name": "test-repo",
        "full_name": "owner/test-repo",
        "stargazers_count": 10,
        "forks_count": 5,
        "open_issues_count": 2,
        "extra_field": "unknown",
    }
    with pytest.raises(ValidationError):
        Repository(**data)


def test_repository_from_api_payload() -> None:
    """from_api_payload should filter unknown fields and create the model."""
    data = {
        "id": 123,
        "name": "test-repo",
        "full_name": "owner/test-repo",
        "stargazers_count": 10,
        "forks_count": 5,
        "open_issues_count": 2,
        "extra_field": "unknown",
        "owner": {"login": "owner"},
    }
    repo = Repository.from_api_payload(data)
    assert repo.id == 123
    assert not hasattr(repo, "extra_field")
    assert not hasattr(repo, "owner")


def test_commit_model_valid() -> None:
    """Commit model should parse valid nested data."""
    data: dict[str, Any] = {
        "sha": "abcdef123456",
        "commit": {
            "author": {
                "name": "Test User",
                "email": "test@example.com",
                "date": "2023-01-01T00:00:00Z",
            },
            "message": "Initial commit",
        },
    }
    commit = Commit(**data)
    assert commit.sha == "abcdef123456"
    assert commit.commit.message == "Initial commit"
    assert commit.commit.author.name == "Test User"


def test_commit_from_api_payload() -> None:
    """from_api_payload should filter unknown fields deeply."""
    data: dict[str, Any] = {
        "sha": "abcdef123456",
        "node_id": "MDY6Q29tbWl0",
        "commit": {
            "author": {
                "name": "Test User",
                "email": "test@example.com",
                "date": "2023-01-01T00:00:00Z",
                "unknown_author_field": True,
            },
            "message": "Initial commit",
            "tree": {"sha": "123"},
            "comment_count": 0,
        },
        "url": "https://api.github.com/...",
        "html_url": "https://github.com/...",
    }
    commit = Commit.from_api_payload(data)
    assert commit.sha == "abcdef123456"
    assert not hasattr(commit, "node_id")
    assert not hasattr(commit.commit, "tree")
    assert not hasattr(commit.commit.author, "unknown_author_field")
    assert commit.commit.message == "Initial commit"

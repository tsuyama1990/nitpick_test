from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from src.domain_models import CommitRecord, RepositoryMetadata


def test_repository_metadata_valid() -> None:
    data = {
        "owner": "test_owner",
        "repo": "test_repo",
        "stargazers_count": 10,
        "forks_count": 5,
        "open_issues_count": 2,
    }
    model = RepositoryMetadata(**data)  # type: ignore[arg-type]
    assert model.owner == "test_owner"
    assert model.stargazers_count == 10


def test_repository_metadata_invalid_negative() -> None:
    data = {
        "owner": "test_owner",
        "repo": "test_repo",
        "stargazers_count": -1,
        "forks_count": 5,
        "open_issues_count": 2,
    }
    with pytest.raises(ValidationError):
        RepositoryMetadata(**data)  # type: ignore[arg-type]


def test_repository_metadata_extra_fields() -> None:
    data = {
        "owner": "test_owner",
        "repo": "test_repo",
        "stargazers_count": 10,
        "forks_count": 5,
        "open_issues_count": 2,
        "extra_field": "not_allowed",
    }
    with pytest.raises(ValidationError):
        RepositoryMetadata(**data)  # type: ignore[arg-type]


def test_commit_record_valid() -> None:
    data = {"sha": "abcdef123456", "author_name": "Test Author", "date": "2023-10-25T10:00:00Z"}
    model = CommitRecord(**data)  # type: ignore[arg-type]
    assert model.sha == "abcdef123456"
    assert model.author_name == "Test Author"
    assert model.date == datetime(2023, 10, 25, 10, 0, 0, tzinfo=UTC)


def test_commit_record_empty_sha() -> None:
    data = {"sha": "", "author_name": "Test Author", "date": "2023-10-25T10:00:00Z"}
    with pytest.raises(ValidationError):
        CommitRecord(**data)  # type: ignore[arg-type]

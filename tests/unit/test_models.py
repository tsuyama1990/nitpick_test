from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from src.domain_models import CommitRecord, RepositoryMetadata


def test_repository_metadata_valid() -> None:
    data: dict[str, object] = {
        "owner": "streamlit",
        "name": "streamlit",
        "stargazers_count": 35000,
        "forks_count": 3000,
        "open_issues_count": 100,
    }
    model = RepositoryMetadata(**data)  # type: ignore[arg-type]
    assert model.owner == "streamlit"
    assert model.stargazers_count == 35000


def test_repository_metadata_invalid_extra() -> None:
    data: dict[str, object] = {
        "owner": "streamlit",
        "name": "streamlit",
        "stargazers_count": 35000,
        "forks_count": 3000,
        "open_issues_count": 100,
        "extra_field": "not allowed",
    }
    with pytest.raises(ValidationError):
        RepositoryMetadata(**data)  # type: ignore[arg-type]


def test_repository_metadata_invalid_negative() -> None:
    data: dict[str, object] = {
        "owner": "streamlit",
        "name": "streamlit",
        "stargazers_count": -1,
        "forks_count": 3000,
        "open_issues_count": 100,
    }
    with pytest.raises(ValidationError):
        RepositoryMetadata(**data)  # type: ignore[arg-type]


def test_commit_record_valid() -> None:
    data: dict[str, object] = {
        "sha": "1234567890abcdef",
        "author_name": "Test Author",
        "date": "2023-01-01T12:00:00Z",
    }
    model = CommitRecord(**data)  # type: ignore[arg-type]
    assert model.sha == "1234567890abcdef"
    assert model.date == datetime(2023, 1, 1, 12, 0, tzinfo=UTC)


def test_commit_record_invalid() -> None:
    data: dict[str, object] = {
        "sha": "1234567890abcdef",
        "author_name": "Test Author",
        "date": "not-a-date",
    }
    with pytest.raises(ValidationError):
        CommitRecord(**data)  # type: ignore[arg-type]

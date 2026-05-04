from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from src.domain_models import CommitRecord, RepositoryMetadata


def test_repository_metadata_valid() -> None:
    data: dict[str, object] = {
        "name": "streamlit",
        "owner": "streamlit",
        "stargazers_count": 1000,
        "forks_count": 500,
        "open_issues_count": 10,
    }
    model = RepositoryMetadata(**data)  # type: ignore[arg-type]
    assert model.name == "streamlit"
    assert model.stargazers_count == 1000


def test_repository_metadata_invalid_negative_stars() -> None:
    data: dict[str, object] = {
        "name": "streamlit",
        "owner": "streamlit",
        "stargazers_count": -1,
        "forks_count": 500,
        "open_issues_count": 10,
    }
    with pytest.raises(ValidationError):
        RepositoryMetadata(**data)  # type: ignore[arg-type]


def test_repository_metadata_forbids_extra() -> None:
    data: dict[str, object] = {
        "name": "streamlit",
        "owner": "streamlit",
        "stargazers_count": 1000,
        "forks_count": 500,
        "open_issues_count": 10,
        "extra_field": "not allowed",
    }
    with pytest.raises(ValidationError):
        RepositoryMetadata(**data)  # type: ignore[arg-type]


def test_commit_record_valid() -> None:
    now = datetime.now(UTC)
    data: dict[str, object] = {
        "sha": "abcdef123456",
        "author_name": "John Doe",
        "date": now,
    }
    model = CommitRecord(**data)  # type: ignore[arg-type]
    assert model.sha == "abcdef123456"
    assert model.author_name == "John Doe"
    assert model.date == now


def test_commit_record_forbids_extra() -> None:
    now = datetime.now(UTC)
    data: dict[str, object] = {
        "sha": "abcdef123456",
        "author_name": "John Doe",
        "date": now,
        "extra": "value",
    }
    with pytest.raises(ValidationError):
        CommitRecord(**data)  # type: ignore[arg-type]

from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from src.domain_models import CommitRecord, RepositoryMetadata


def test_repository_metadata_valid() -> None:
    data: dict[str, Any] = {
        "name": "streamlit",
        "owner": "streamlit",
        "stargazers_count": 30000,
        "forks_count": 5000,
        "open_issues_count": 200,
    }
    repo = RepositoryMetadata(**data)
    assert repo.name == "streamlit"
    assert repo.stargazers_count == 30000


def test_repository_metadata_invalid_counts() -> None:
    data: dict[str, Any] = {
        "name": "streamlit",
        "owner": "streamlit",
        "stargazers_count": -1,
        "forks_count": 0,
        "open_issues_count": 0,
    }
    with pytest.raises(ValidationError):
        RepositoryMetadata(**data)


def test_repository_metadata_extra_fields() -> None:
    data: dict[str, Any] = {
        "name": "streamlit",
        "owner": "streamlit",
        "stargazers_count": 10,
        "forks_count": 0,
        "open_issues_count": 0,
        "extra_field": "not allowed",
    }
    with pytest.raises(ValidationError):
        RepositoryMetadata(**data)


def test_commit_record_valid() -> None:
    data: dict[str, Any] = {
        "sha": "abcdef123456",
        "author_name": "Linus Torvalds",
        "date": "2023-10-27T10:00:00Z",
    }
    commit = CommitRecord(**data)
    assert commit.sha == "abcdef123456"
    assert commit.author_name == "Linus Torvalds"
    assert commit.date == datetime(2023, 10, 27, 10, 0, tzinfo=UTC)

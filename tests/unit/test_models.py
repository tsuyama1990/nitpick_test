from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from src.domain_models import CommitRecord, RepositoryMetadata


def test_repository_metadata_valid() -> None:
    data = {
        "owner": {"login": "streamlit"},
        "name": "streamlit",
        "stargazers_count": 100,
        "forks_count": 10,
        "open_issues_count": 5,
    }
    repo = RepositoryMetadata(**data)  # type: ignore[arg-type]
    assert repo.owner == "streamlit"
    assert repo.name == "streamlit"
    assert repo.stargazers_count == 100


def test_repository_metadata_invalid_negative() -> None:
    data = {
        "owner": {"login": "streamlit"},
        "name": "streamlit",
        "stargazers_count": -1,
        "forks_count": 10,
        "open_issues_count": 5,
    }
    with pytest.raises(ValidationError):
        RepositoryMetadata(**data)  # type: ignore[arg-type]


def test_commit_record_valid() -> None:
    data = {
        "sha": "abcdef123456",
        "commit": {"author": {"name": "John Doe", "date": "2023-10-01T12:00:00Z"}},
    }
    commit = CommitRecord(**data)  # type: ignore[arg-type]
    assert commit.sha == "abcdef123456"
    assert commit.author_name == "John Doe"
    assert commit.timestamp == datetime(2023, 10, 1, 12, 0, tzinfo=UTC)

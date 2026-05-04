from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from src.domain_models import CommitRecord, RepositoryMetadata


def test_repository_metadata_valid() -> None:
    data: dict[str, Any] = {
        "owner": "streamlit",
        "name": "streamlit",
        "stargazers_count": 100,
        "forks_count": 50,
        "open_issues_count": 10,
    }
    repo = RepositoryMetadata(**data)
    assert repo.owner == "streamlit"
    assert repo.name == "streamlit"
    assert repo.star_count == 100
    assert repo.fork_count == 50
    assert repo.open_issue_count == 10


def test_repository_metadata_invalid_star_count() -> None:
    with pytest.raises(ValidationError):
        RepositoryMetadata(
            owner="streamlit",
            name="streamlit",
            stargazers_count=-1,
            forks_count=50,
            open_issues_count=10,
        )


def test_commit_record_valid() -> None:
    data: dict[str, Any] = {
        "sha": "abcdef",
        "commit": {
            "author": {
                "name": "John Doe",
                "date": "2023-01-01T00:00:00Z",
            }
        },
    }
    commit = CommitRecord(**data)
    assert commit.sha == "abcdef"
    assert commit.author_name == "John Doe"
    assert commit.timestamp == datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC)

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from src.domain_models import CommitRecord, RepositoryMetadata


def test_repository_metadata_valid() -> None:
    repo = RepositoryMetadata(
        owner="streamlit",
        repo="streamlit",
        stars=1000,
        forks=200,
        open_issues=50,
    )
    assert repo.owner == "streamlit"
    assert repo.stars == 1000


def test_repository_metadata_invalid_stars() -> None:
    with pytest.raises(ValidationError):
        RepositoryMetadata(
            owner="streamlit",
            repo="streamlit",
            stars=-5,
            forks=200,
            open_issues=50,
        )


def test_commit_record_valid() -> None:
    dt = datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC)
    commit = CommitRecord(
        commit_hash="abcdef123456",
        author_name="John Doe",
        timestamp=dt,
    )
    assert commit.commit_hash == "abcdef123456"
    assert commit.timestamp == dt


def test_commit_record_invalid_timestamp() -> None:
    with pytest.raises(ValidationError):
        CommitRecord(
            commit_hash="abcdef123456",
            author_name="John Doe",
            timestamp="not-a-timestamp",  # type: ignore[arg-type]
        )

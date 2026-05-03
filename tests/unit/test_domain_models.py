from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from src.domain_models import CommitRecord, RepositoryMetadata


def test_repository_metadata_valid() -> None:
    repo = RepositoryMetadata(
        owner="octocat", name="Hello-World", star_count=10, fork_count=5, open_issue_count=2
    )
    assert repo.owner == "octocat"
    assert repo.star_count == 10


def test_repository_metadata_invalid_stars() -> None:
    with pytest.raises(ValidationError):
        RepositoryMetadata(
            owner="octocat", name="Hello-World", star_count=-1, fork_count=5, open_issue_count=2
        )


def test_repository_metadata_extra_forbid() -> None:
    with pytest.raises(ValidationError):
        RepositoryMetadata(
            owner="octocat",
            name="Hello-World",
            star_count=10,
            fork_count=5,
            open_issue_count=2,
            extra_field="bad", # type: ignore[call-arg]
        )


def test_commit_record_valid() -> None:
    commit = CommitRecord(
        commit_hash="abc1234", author="alice", date=datetime(2023, 1, 1, tzinfo=UTC)
    )
    assert commit.commit_hash == "abc1234"
    assert commit.author == "alice"


def test_commit_record_extra_forbid() -> None:
    with pytest.raises(ValidationError):
        CommitRecord(
            commit_hash="abc1234",
            author="alice",
            date=datetime(2023, 1, 1, tzinfo=UTC),
            extra_field="bad", # type: ignore[call-arg]
        )

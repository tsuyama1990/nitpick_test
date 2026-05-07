from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from src.domain_models.github import Commit, Repository


def test_repository_success() -> None:
    repo = Repository(stargazers_count=10, forks_count=5, open_issues_count=2)
    assert repo.stargazers_count == 10
    assert repo.forks_count == 5
    assert repo.open_issues_count == 2


def test_repository_ignores_extra() -> None:
    repo = Repository(stargazers_count=1, forks_count=1, open_issues_count=1, extra_field="foo")  # type: ignore[call-arg]
    assert not hasattr(repo, "extra_field")


def test_repository_invalid_negative() -> None:
    with pytest.raises(ValidationError):
        Repository(stargazers_count=-1, forks_count=0, open_issues_count=0)


def test_commit_success() -> None:
    dt = datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC)
    commit = Commit(sha="abc1234", commit={"committer": {"name": "Alice", "date": dt}})  # type: ignore[arg-type]
    assert commit.sha == "abc1234"
    assert commit.commit.committer.name == "Alice"
    assert commit.commit.committer.date == dt


def test_commit_invalid_empty_sha() -> None:
    with pytest.raises(ValidationError):
        Commit(
            sha="",
            commit={  # type: ignore[arg-type]
                "committer": {"name": "Alice", "date": datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC)}
            },
        )

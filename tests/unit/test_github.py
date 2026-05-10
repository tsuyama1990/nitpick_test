from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from src.domain_models.github import CommitDetails, CommitInfo, Committer, RepoInfo


def test_repo_info_valid() -> None:
    data = {
        "stargazers_count": 100,
        "forks_count": 50,
        "open_issues_count": 10,
        "extra_field": "should be stripped",
    }
    repo = RepoInfo(**data)  # type: ignore[arg-type]
    assert repo.stargazers_count == 100
    assert repo.forks_count == 50
    assert repo.open_issues_count == 10
    assert not hasattr(repo, "extra_field")


def test_repo_info_invalid() -> None:
    data = {"stargazers_count": -1, "forks_count": 50, "open_issues_count": 10}
    with pytest.raises(ValidationError):
        RepoInfo(**data)


def test_committer_valid() -> None:
    data = {
        "name": "Alice",
        "date": "2023-01-01T12:00:00Z",
        "email": "alice@example.com",  # Should be stripped
    }
    committer = Committer(**data)  # type: ignore[arg-type]
    assert committer.name == "Alice"
    assert committer.date == datetime(2023, 1, 1, 12, 0, tzinfo=UTC)
    assert not hasattr(committer, "email")


def test_committer_invalid() -> None:
    data = {"name": "", "date": "2023-01-01T12:00:00Z"}
    with pytest.raises(ValidationError):
        Committer(**data)  # type: ignore[arg-type]


def test_commit_details_valid() -> None:
    data = {
        "committer": {"name": "Bob", "date": "2023-01-01T12:00:00Z"},
        "message": "Initial commit",
        "tree": {"sha": "123"},  # Stripped
    }
    details = CommitDetails(**data)  # type: ignore[arg-type]
    assert details.committer.name == "Bob"
    assert details.message == "Initial commit"
    assert not hasattr(details, "tree")


def test_commit_info_valid() -> None:
    data = {
        "sha": "abc12345",
        "commit": {
            "committer": {"name": "Charlie", "date": "2023-01-01T12:00:00Z"},
            "message": "Fix bug",
        },
        "author": {"login": "charlie"},  # Stripped
    }
    info = CommitInfo(**data)  # type: ignore[arg-type]
    assert info.sha == "abc12345"
    assert info.commit.committer.name == "Charlie"
    assert not hasattr(info, "author")

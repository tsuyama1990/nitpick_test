from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from src.domain_models.github import CommitInfo, RepoInfo


def test_repo_info_valid() -> None:
    data: dict[str, object] = {"stargazers_count": 100, "forks_count": 50, "open_issues_count": 10, "extra_field": "ignore_me"}
    info = RepoInfo(**data) # type: ignore[arg-type]
    assert info.stargazers_count == 100
    assert info.forks_count == 50
    assert info.open_issues_count == 10

def test_repo_info_invalid() -> None:
    with pytest.raises(ValidationError):
        RepoInfo(stargazers_count=-1, forks_count=50, open_issues_count=10)

def test_commit_info_flattening() -> None:
    data: dict[str, object] = {
        "sha": "12345",
        "commit": {
            "author": {
                "name": "Test User",
                "date": "2023-10-27T10:00:00Z"
            },
            "message": "Test commit"
        }
    }
    info = CommitInfo(**data) # type: ignore[arg-type]
    assert info.name == "Test User"
    assert info.date == datetime(2023, 10, 27, 10, 0, tzinfo=UTC)

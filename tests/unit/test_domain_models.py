import pytest
from pydantic import ValidationError

from src.domain_models import CommitData, RepositoryInfo


def test_repository_info_validation() -> None:
    # extra="ignore" allows extra fields to be discarded
    data: dict[str, object] = {
        "stargazers_count": 100,
        "forks_count": 50,
        "open_issues_count": 5,
        "extra_field": "should be ignored",
    }
    repo = RepositoryInfo(**data)  # type: ignore[arg-type]
    assert repo.stargazers_count == 100
    assert repo.forks_count == 50
    assert repo.open_issues_count == 5
    assert not hasattr(repo, "extra_field")

    # Missing fields should raise ValidationError
    with pytest.raises(ValidationError):
        RepositoryInfo(stargazers_count=100)  # type: ignore[call-arg]


def test_commit_data_flattening() -> None:
    payload: dict[str, object] = {
        "sha": "12345",
        "commit": {
            "author": {"name": "Octocat", "date": "2023-01-01T12:00:00Z"},
            "message": "Initial commit",
        },
        "extra": "ignored",
    }
    commit = CommitData(**payload)  # type: ignore[arg-type]
    assert commit.author_name == "Octocat"
    assert commit.date.tzinfo is not None  # Should parse correctly with timezone info
    assert commit.date.year == 2023
    assert not hasattr(commit, "extra")

    # If missing required nested fields, should raise ValidationError
    bad_payload: dict[str, object] = {"sha": "12345", "commit": {}}
    with pytest.raises(ValidationError):
        CommitData(**bad_payload)  # type: ignore[arg-type]

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from src.domain_models import CommitRecord, RepositoryMetadata


def test_repository_metadata_valid() -> None:
    data = {
        "owner": {"login": "testowner"},
        "name": "testrepo",
        "stargazers_count": 100,
        "forks_count": 50,
        "open_issues_count": 5,
    }
    model = RepositoryMetadata.model_validate(data)
    assert model.owner == "testowner"
    assert model.repo_name == "testrepo"
    assert model.star_count == 100
    assert model.fork_count == 50
    assert model.open_issue_count == 5


def test_repository_metadata_invalid_negative_counts() -> None:
    data = {
        "owner": {"login": "testowner"},
        "name": "testrepo",
        "stargazers_count": -1,
        "forks_count": 50,
        "open_issues_count": 5,
    }
    with pytest.raises(ValidationError):
        RepositoryMetadata.model_validate(data)


def test_repository_metadata_invalid_extra_field() -> None:
    data = {
        "owner": {"login": "testowner"},
        "name": "testrepo",
        "stargazers_count": 100,
        "forks_count": 50,
        "open_issues_count": 5,
        "extra_field": "should_be_forbidden",
    }
    with pytest.raises(ValidationError):
        RepositoryMetadata.model_validate(data)


def test_commit_record_valid() -> None:
    data = {
        "sha": "abcdef123456",
        "commit": {"author": {"name": "John Doe", "date": "2023-01-01T12:00:00Z"}},
    }
    model = CommitRecord.model_validate(data)
    assert model.sha == "abcdef123456"
    assert model.author_name == "John Doe"
    assert model.date == datetime(2023, 1, 1, 12, 0, tzinfo=UTC)


def test_commit_record_invalid_missing_fields() -> None:
    data = {"sha": "abcdef123456"}
    with pytest.raises(ValidationError):
        CommitRecord.model_validate(data)

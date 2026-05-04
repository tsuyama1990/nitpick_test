from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from src.domain_models.models import CommitRecord, RepositoryMetadata


def test_repository_metadata_valid() -> None:
    data = {
        "owner": "streamlit",
        "repo": "streamlit",
        "star_count": 100,
        "fork_count": 10,
        "open_issue_count": 5,
    }
    model = RepositoryMetadata(**data)  # type: ignore[arg-type]
    assert model.owner == "streamlit"
    assert model.repo == "streamlit"
    assert model.star_count == 100
    assert model.fork_count == 10
    assert model.open_issue_count == 5


def test_repository_metadata_invalid_negative_counts() -> None:
    data = {
        "owner": "streamlit",
        "repo": "streamlit",
        "star_count": -1,
        "fork_count": 10,
        "open_issue_count": 5,
    }
    with pytest.raises(ValidationError):
        RepositoryMetadata(**data)  # type: ignore[arg-type]


def test_repository_metadata_extra_fields() -> None:
    data = {
        "owner": "streamlit",
        "repo": "streamlit",
        "star_count": 100,
        "fork_count": 10,
        "open_issue_count": 5,
        "extra_field": "not_allowed",
    }
    with pytest.raises(ValidationError):
        RepositoryMetadata(**data)  # type: ignore[arg-type]


def test_commit_record_valid_datetime() -> None:
    data = {"commit_hash": "abcdef", "author_name": "Jules", "timestamp": datetime.now(UTC)}
    model = CommitRecord(**data)  # type: ignore[arg-type]
    assert model.commit_hash == "abcdef"
    assert model.author_name == "Jules"
    assert isinstance(model.timestamp, datetime)


def test_commit_record_valid_string_datetime() -> None:
    data = {"commit_hash": "abcdef", "author_name": "Jules", "timestamp": "2023-10-10T10:10:10Z"}
    model = CommitRecord(**data)  # type: ignore[arg-type]
    assert model.commit_hash == "abcdef"
    assert isinstance(model.timestamp, datetime)


def test_commit_record_extra_fields() -> None:
    data = {
        "commit_hash": "abcdef",
        "author_name": "Jules",
        "timestamp": "2023-10-10T10:10:10Z",
        "extra_field": "not_allowed",
    }
    with pytest.raises(ValidationError):
        CommitRecord(**data)  # type: ignore[arg-type]

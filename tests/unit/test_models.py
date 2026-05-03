from datetime import datetime

import pytest
from pydantic import ValidationError

from src.domain.models import CommitRecord, RepositoryMetadata


def test_repository_metadata_valid() -> None:
    data = {
        "name": "streamlit",
        "owner": "streamlit",
        "stargazers_count": 30000,
        "forks_count": 2000,
        "open_issues_count": 150
    }
    repo = RepositoryMetadata.model_validate(data)
    assert repo.name == "streamlit"
    assert repo.stargazers_count == 30000

def test_repository_metadata_invalid_counts() -> None:
    data = {
        "name": "streamlit",
        "owner": "streamlit",
        "stargazers_count": -1,
        "forks_count": 2000,
        "open_issues_count": 150
    }
    with pytest.raises(ValidationError):
        RepositoryMetadata.model_validate(data)

def test_repository_metadata_extra_fields() -> None:
    data = {
        "name": "streamlit",
        "owner": "streamlit",
        "stargazers_count": 30000,
        "forks_count": 2000,
        "open_issues_count": 150,
        "extra_field": "not allowed"
    }
    with pytest.raises(ValidationError):
        RepositoryMetadata.model_validate(data)

def test_commit_record_valid() -> None:
    data = {
        "sha": "1234567890abcdef",
        "author_name": "Test User",
        "date": "2023-01-01T10:00:00Z"
    }
    commit = CommitRecord.model_validate(data)
    assert commit.sha == "1234567890abcdef"
    assert isinstance(commit.date, datetime)

def test_commit_record_invalid_date() -> None:
    data = {
        "sha": "1234567890abcdef",
        "author_name": "Test User",
        "date": "invalid-date"
    }
    with pytest.raises(ValidationError):
        CommitRecord.model_validate(data)

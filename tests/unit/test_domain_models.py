from datetime import datetime

import pytest
from pydantic import ValidationError

from src.domain_models.commit import CommitData
from src.domain_models.repository import RepositoryInfo


def test_repository_info_massive_json() -> None:
    """Test RepositoryInfo safely ignores extra fields from a massive JSON payload."""
    data = {
        "name": "streamlit",
        "owner": "streamlit",  # Real API has an object, but spec says `owner` (str). Let's use str for now. Wait, GitHub API returns `owner: { login: 'streamlit' }`.
        # Spec says: Fields: name (str), owner (str), stargazers_count (int), forks_count (int), open_issues_count (int).
        # We will map it in RepositoryInfo if necessary, or just follow the spec as flat if the spec doesn't require pre-validator here.
        "stargazers_count": 1000,
        "forks_count": 500,
        "open_issues_count": 100,
        "extra_field_1": "ignore me",
        "extra_field_2": {"nested": "ignore me too"},
        "id": 1234567,
        "node_id": "MDEwOlJlcG9zaXRvcnk=",
    }

    repo_info = RepositoryInfo(**data)  # type: ignore[arg-type]

    assert repo_info.name == "streamlit"
    assert repo_info.owner == "streamlit"
    assert repo_info.stargazers_count == 1000
    assert repo_info.forks_count == 500
    assert repo_info.open_issues_count == 100

    # Assert extra fields are not present as attributes
    assert not hasattr(repo_info, "extra_field_1")


def test_commit_data_nested_json() -> None:
    """Test CommitData pre-validator flattens nested GitHub API payload."""
    payload = {
        "sha": "1234567890abcdef",
        "commit": {
            "author": {
                "name": "John Doe",
                "email": "john@example.com",
                "date": "2023-01-01T12:00:00Z"
            },
            "message": "Initial commit"
        },
        "url": "https://api.github.com/repos/.../commits/...",
    }

    commit = CommitData.model_validate(payload)

    assert commit.sha == "1234567890abcdef"
    assert commit.author_name == "John Doe"
    assert isinstance(commit.date, datetime)
    assert commit.date.year == 2023
    assert commit.date.month == 1
    assert commit.date.day == 1


def test_commit_data_invalid_payload() -> None:
    """Test CommitData raises ValidationError when required nested fields are missing."""
    payload = {
        "sha": "1234567890abcdef",
        "commit": {
            # Missing author node entirely
        }
    }
    with pytest.raises(ValidationError):
        CommitData.model_validate(payload)

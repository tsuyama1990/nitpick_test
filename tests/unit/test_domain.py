from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from src.domain_models import (
    CommitItem,
    GitHubAnalyticsError,
    RateLimitExceededError,
    RepositoryMetrics,
    RepositoryNotFoundError,
)


def test_github_analytics_exceptions() -> None:
    """Test domain exceptions can be raised with informative messages."""
    msg1 = "Base error"
    err1 = GitHubAnalyticsError(msg1)
    assert str(err1) == msg1

    msg2 = "Not found"
    err2 = RepositoryNotFoundError(msg2)
    assert str(err2) == msg2
    assert isinstance(err2, GitHubAnalyticsError)

    msg3 = "Rate limited"
    err3 = RateLimitExceededError(msg3)
    assert str(err3) == msg3
    assert isinstance(err3, GitHubAnalyticsError)


def test_repository_metrics_validation() -> None:
    """Test valid repository metrics parsing and stripping unknown fields."""
    raw_data: dict[str, Any] = {
        "stargazers_count": 100,
        "forks_count": 20,
        "open_issues_count": 5,
        "extra_field_to_strip": "should be ignored",
        "another_extra": 123,
    }

    metrics = RepositoryMetrics(**raw_data)

    assert metrics.stargazers_count == 100
    assert metrics.forks_count == 20
    assert metrics.open_issues_count == 5
    assert not hasattr(metrics, "extra_field_to_strip")


def test_repository_metrics_rejection() -> None:
    """Test repository metrics rejects invalid data."""
    # Missing field
    missing_data: dict[str, Any] = {"stargazers_count": 100, "forks_count": 20}
    with pytest.raises(ValidationError):
        RepositoryMetrics(**missing_data)

    # Invalid type
    invalid_data: dict[str, Any] = {
        "stargazers_count": "invalid",
        "forks_count": 20,
        "open_issues_count": 5,
    }
    with pytest.raises(ValidationError):
        RepositoryMetrics(**invalid_data)


def test_commit_item_validation() -> None:
    """Test valid commit item parsing, ensuring ISO 8601 strings become datetimes and extra fields are stripped."""
    raw_data: dict[str, Any] = {
        "sha": "abcdef",  # Extra field at root
        "commit": {
            "author": {
                "name": "Jane Doe",
                "date": "2023-10-01T12:00:00Z",
                "email": "jane@example.com",  # Extra field inside author
            },
            "message": "Fix bug",  # Extra field inside commit
            "tree": {"sha": "123"},  # Extra field inside commit
        },
        "url": "https://api.github.com/...",  # Extra field at root
    }

    item = CommitItem(**raw_data)

    # Assert data mapping
    assert item.commit.author.name == "Jane Doe"

    # Assert datetime parsing
    expected_date = datetime(2023, 10, 1, 12, 0, tzinfo=UTC)
    assert item.commit.author.date == expected_date

    # Assert extra fields are stripped
    assert not hasattr(item, "sha")
    assert not hasattr(item.commit, "message")
    assert not hasattr(item.commit.author, "email")


def test_commit_item_rejection() -> None:
    """Test commit item rejects missing or invalid fields."""
    # Missing nested author name
    missing_data: dict[str, Any] = {
        "commit": {
            "author": {
                "date": "2023-10-01T12:00:00Z",
            }
        }
    }
    with pytest.raises(ValidationError):
        CommitItem(**missing_data)

    # Invalid date format
    invalid_data: dict[str, Any] = {
        "commit": {
            "author": {
                "name": "Jane Doe",
                "date": "invalid-date",
            }
        }
    }
    with pytest.raises(ValidationError):
        CommitItem(**invalid_data)


def test_domain_model_validation_non_dict() -> None:
    """Test model validation gracefully handles non-dict payloads."""
    with pytest.raises(ValidationError):
        RepositoryMetrics.model_validate("not-a-dict")

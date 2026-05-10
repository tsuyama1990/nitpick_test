from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from src.domain_models import (
    CommitItem,
    RepositoryMetrics,
)


def test_repository_metrics_valid() -> None:
    """Test valid instantiation of RepositoryMetrics."""
    data = {
        "stargazers_count": 100,
        "forks_count": 50,
        "open_issues_count": 10,
        "extra_field": "should_be_stripped"
    }
    metrics = RepositoryMetrics(**data)  # type: ignore[arg-type]

    assert metrics.stargazers_count == 100
    assert metrics.forks_count == 50
    assert metrics.open_issues_count == 10
    assert not hasattr(metrics, "extra_field")


def test_repository_metrics_invalid() -> None:
    """Test invalid types raise ValidationError for RepositoryMetrics."""
    data = {
        "stargazers_count": "string",
        "forks_count": 50,
        "open_issues_count": 10,
    }
    with pytest.raises(ValidationError):
        RepositoryMetrics(**data)  # type: ignore[arg-type]


def test_commit_item_valid() -> None:
    """Test valid instantiation and parsing of nested CommitItem."""
    data = {
        "commit": {
            "author": {
                "name": "Octocat",
                "date": "2023-10-01T12:00:00Z",
                "email": "octocat@github.com"  # extra field
            },
            "message": "Initial commit"  # extra field
        },
        "url": "https://api.github.com/repos/octocat/Hello-World/commits/sha" # extra field
    }

    item = CommitItem(**data)  # type: ignore[arg-type]

    assert item.commit.author.name == "Octocat"
    assert item.commit.author.date == datetime(2023, 10, 1, 12, 0, 0, tzinfo=UTC)
    assert not hasattr(item, "url")
    assert not hasattr(item.commit, "message")
    assert not hasattr(item.commit.author, "email")


def test_commit_item_invalid() -> None:
    """Test missing required field raises ValidationError for CommitItem."""
    data: dict[str, Any] = {
        "commit": {
            "author": {
                "date": "2023-10-01T12:00:00Z"
            }
        }
    }
    with pytest.raises(ValidationError):
        CommitItem(**data)

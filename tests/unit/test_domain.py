import os
from datetime import UTC, datetime
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from src.domain_models import (
    CommitItem,
    RepositoryMetrics,
    Settings,
    get_settings,
)


def test_repository_metrics_valid() -> None:
    """Test RepositoryMetrics with valid data."""
    data = {
        "stargazers_count": 100,
        "forks_count": 50,
        "open_issues_count": 10,
        "extra_field": "should be stripped",
    }
    metrics = RepositoryMetrics(**data)  # type: ignore[arg-type]
    assert metrics.stargazers_count == 100
    assert metrics.forks_count == 50
    assert metrics.open_issues_count == 10
    assert not hasattr(metrics, "extra_field")


def test_repository_metrics_invalid() -> None:
    """Test RepositoryMetrics with invalid data."""
    data = {
        "stargazers_count": "invalid",
        "forks_count": 50,
        "open_issues_count": 10,
    }
    with pytest.raises(ValidationError):
        RepositoryMetrics(**data)  # type: ignore[arg-type]


def test_commit_item_valid() -> None:
    """Test CommitItem with valid data."""
    data = {
        "commit": {
            "author": {
                "name": "Test User",
                "date": "2023-10-01T12:00:00Z",
                "extra_author_field": "stripped",
            },
            "extra_commit_field": "stripped",
        },
        "extra_item_field": "stripped",
    }
    item = CommitItem(**data)  # type: ignore[arg-type]
    assert item.commit.author.name == "Test User"
    assert item.commit.author.date == datetime(2023, 10, 1, 12, 0, tzinfo=UTC)
    assert not hasattr(item.commit.author, "extra_author_field")
    assert not hasattr(item.commit, "extra_commit_field")
    assert not hasattr(item, "extra_item_field")


def test_commit_item_invalid_missing_author() -> None:
    """Test CommitItem with missing required field."""
    data = {
        "commit": {
            "author": {
                "date": "2023-10-01T12:00:00Z",
            }
        }
    }
    with pytest.raises(ValidationError):
        CommitItem(**data)  # type: ignore[arg-type]


@patch.dict(os.environ, {"GITHUB_TOKEN": "dummy_token"}, clear=True)
def test_settings_valid() -> None:
    """Test Settings with valid environment variable."""
    get_settings.cache_clear()
    settings = get_settings()
    assert settings.GITHUB_TOKEN == "dummy_token"  # noqa: S105


@patch.dict(os.environ, {}, clear=True)
def test_settings_invalid_missing_token() -> None:
    """Test Settings without required environment variable."""
    get_settings.cache_clear()
    with pytest.raises(ValidationError):
        Settings()  # type: ignore[call-arg]

"""Unit tests for the domain models and configuration."""

import os
from datetime import UTC, datetime
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from src.domain_models.config import Settings, get_settings
from src.domain_models.schemas import CommitItem, RepositoryMetrics


def test_repository_metrics_valid() -> None:
    """Test valid repository metrics."""
    data = {
        "stargazers_count": 100,
        "forks_count": 50,
        "open_issues_count": 10,
        "extra_field": "should_be_ignored",
    }
    metrics = RepositoryMetrics(**data)  # type: ignore[arg-type]
    assert metrics.stargazers_count == 100
    assert metrics.forks_count == 50
    assert metrics.open_issues_count == 10
    assert not hasattr(metrics, "extra_field")


def test_repository_metrics_invalid() -> None:
    """Test invalid repository metrics."""
    data = {
        "stargazers_count": "not_an_int",
        "forks_count": 50,
    }
    with pytest.raises(ValidationError):
        RepositoryMetrics(**data)  # type: ignore[arg-type]


def test_commit_item_valid() -> None:
    """Test valid commit item."""
    data = {
        "commit": {
            "author": {
                "name": "Test User",
                "date": "2023-01-01T12:00:00Z",
                "email": "test@example.com",  # Should be stripped
            },
            "message": "Test commit",  # Should be stripped
        },
        "sha": "123456",  # Should be stripped
    }
    item = CommitItem(**data)  # type: ignore[arg-type]
    assert item.commit.author.name == "Test User"
    assert item.commit.author.date == datetime(2023, 1, 1, 12, 0, tzinfo=UTC)


def test_commit_item_invalid() -> None:
    """Test invalid commit item."""
    data = {
        "commit": {
            "author": {
                "name": "Test User",
            }
        }
    }
    with pytest.raises(ValidationError):
        CommitItem(**data)  # type: ignore[arg-type]


def test_settings_valid() -> None:
    """Test settings with valid environment."""
    get_settings.cache_clear()
    with patch.dict(os.environ, {"GITHUB_TOKEN": "valid_token"}):
        settings = get_settings()
        assert settings.GITHUB_TOKEN == "valid_token"  # noqa: S105


def test_settings_invalid() -> None:
    """Test settings with missing environment variable."""
    get_settings.cache_clear()
    with patch.dict(os.environ, {}, clear=True), pytest.raises(ValidationError):
        Settings()  # type: ignore[call-arg]


def test_strip_extra_non_dict() -> None:
    """Test that _strip_extra returns the data if it is not a dict."""
    data = "not a dict"
    result = CommitItem._strip_extra(data)
    assert result == "not a dict"

"""Unit tests for the domain models."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from src.domain_models.exceptions import (
    GitHubAnalyticsError,
    RateLimitExceededError,
    RepositoryNotFoundError,
)
from src.domain_models.schemas import (
    CommitItem,
    RepositoryMetrics,
)


def test_github_analytics_error_initialization() -> None:
    """Test base exception initialization."""
    err = GitHubAnalyticsError("Base error")
    assert str(err) == "Base error"


def test_repository_not_found_error() -> None:
    """Test RepositoryNotFoundError initialization."""
    err = RepositoryNotFoundError("Repo missing")
    assert isinstance(err, GitHubAnalyticsError)
    assert str(err) == "Repo missing"


def test_rate_limit_exceeded_error() -> None:
    """Test RateLimitExceededError initialization."""
    err = RateLimitExceededError("Rate limit hit")
    assert isinstance(err, GitHubAnalyticsError)
    assert str(err) == "Rate limit hit"


def test_repository_metrics_valid() -> None:
    """Test RepositoryMetrics successfully parses valid data and strips extra fields."""
    data: dict[str, object] = {
        "stargazers_count": 100,
        "forks_count": 50,
        "open_issues_count": 5,
        "unexpected_field": "should_be_stripped",
    }
    metrics = RepositoryMetrics(**data)  # type: ignore[arg-type]
    assert metrics.stargazers_count == 100
    assert metrics.forks_count == 50
    assert metrics.open_issues_count == 5
    assert not hasattr(metrics, "unexpected_field")


def test_repository_metrics_invalid_type() -> None:
    """Test RepositoryMetrics raises ValidationError for invalid types."""
    data = {
        "stargazers_count": "one_hundred",
        "forks_count": 50,
        "open_issues_count": 5,
    }
    with pytest.raises(ValidationError, match="stargazers_count"):
        RepositoryMetrics(**data)  # type: ignore[arg-type]


def test_commit_item_valid() -> None:
    """Test CommitItem successfully parses valid payload and dates."""
    date_str = "2024-05-16T12:00:00Z"
    data: dict[str, object] = {
        "commit": {
            "author": {
                "name": "Jules",
                "date": date_str,
            },
            "extra_data": "stripped",
        },
        "sha": "12345",
    }
    item = CommitItem(**data)  # type: ignore[arg-type]
    assert item.commit.author.name == "Jules"
    # Note: Pydantic parsing creates aware datetimes in recent versions
    expected_dt = datetime(2024, 5, 16, 12, 0, tzinfo=UTC)
    assert item.commit.author.date == expected_dt
    assert not hasattr(item.commit, "extra_data")
    assert not hasattr(item, "sha")


def test_commit_item_missing_author_name() -> None:
    """Test CommitItem raises ValidationError if required fields are missing."""
    data = {
        "commit": {
            "author": {
                "date": "2024-05-16T12:00:00Z",
            }
        }
    }
    with pytest.raises(ValidationError, match="name"):
        CommitItem(**data)  # type: ignore[arg-type]


def test_strip_extra_non_dict() -> None:
    """Test that _strip_extra safely handles non-dict inputs."""
    from src.domain_models.schemas import _strip_extra

    res = _strip_extra("not a dict", {})
    assert res == "not a dict"

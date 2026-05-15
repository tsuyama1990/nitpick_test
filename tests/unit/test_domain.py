import os
import unittest.mock
from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from src.config import get_settings
from src.domain_models.exceptions import (
    GitHubAnalyticsError,
    RateLimitExceededError,
    RepositoryNotFoundError,
)
from src.domain_models.schemas import CommitItem, RepositoryMetrics


def test_repository_metrics_valid_data() -> None:
    data: dict[str, Any] = {
        "stargazers_count": 10,
        "forks_count": 5,
        "open_issues_count": 2,
        "extra_field": "ignore",
    }
    metrics = RepositoryMetrics(**data)
    assert metrics.stargazers_count == 10
    assert metrics.forks_count == 5
    assert metrics.open_issues_count == 2
    assert not hasattr(metrics, "extra_field")


def test_repository_metrics_invalid_data() -> None:
    with pytest.raises(ValidationError):
        RepositoryMetrics(
            stargazers_count="not_an_int",  # type: ignore[arg-type]
            forks_count=5,
            open_issues_count=2,
        )


def test_commit_item_valid_data() -> None:
    data: dict[str, Any] = {
        "commit": {
            "author": {
                "name": "John Doe",
                "date": "2023-10-27T10:00:00Z",
                "extra_author_field": "ignore_me",
            },
            "extra_commit_field": "ignore_me",
        },
        "extra_item_field": "ignore_me",
    }
    item = CommitItem(**data)
    assert item.commit.author.name == "John Doe"
    assert item.commit.author.date == datetime(2023, 10, 27, 10, 0, tzinfo=UTC)
    assert not hasattr(item, "extra_item_field")
    assert not hasattr(item.commit, "extra_commit_field")
    assert not hasattr(item.commit.author, "extra_author_field")


def test_commit_item_invalid_data() -> None:
    data: dict[str, Any] = {
        "commit": {
            "author": {
                # missing name
                "date": "2023-10-27T10:00:00Z"
            }
        }
    }
    with pytest.raises(ValidationError):
        CommitItem(**data)


def test_settings_valid_token() -> None:
    get_settings.cache_clear()
    with unittest.mock.patch.dict(os.environ, {"GITHUB_TOKEN": "valid_token"}):
        settings = get_settings()
        assert settings.GITHUB_TOKEN == "valid_token"  # noqa: S105


def test_settings_missing_token() -> None:
    get_settings.cache_clear()
    with (
        unittest.mock.patch.dict(os.environ, {}, clear=True),
        pytest.raises(ValidationError),
    ):
        get_settings()


def test_exceptions() -> None:
    err = GitHubAnalyticsError("base error")
    assert str(err) == "base error"

    repo_err = RepositoryNotFoundError("repo error")
    assert isinstance(repo_err, GitHubAnalyticsError)
    assert str(repo_err) == "repo error"

    limit_err = RateLimitExceededError("limit error")
    assert isinstance(limit_err, GitHubAnalyticsError)
    assert str(limit_err) == "limit error"

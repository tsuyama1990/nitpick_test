import os
from datetime import datetime
from unittest import mock

import pytest
from pydantic import ValidationError

from src.domain_models.config import Settings, get_settings
from src.domain_models.schemas import (
    CommitItem,
    RepositoryMetrics,
)


@pytest.fixture(autouse=True)
def _clear_cache() -> None:
    get_settings.cache_clear()


def test_settings_with_valid_token() -> None:
    with mock.patch.dict(os.environ, {"GITHUB_TOKEN": "dummy_token"}, clear=True):
        settings = Settings()  # type: ignore[call-arg]
        assert settings.GITHUB_TOKEN == "dummy_token"  # noqa: S105


def test_settings_missing_token() -> None:
    with mock.patch.dict(os.environ, {}, clear=True), pytest.raises(ValidationError):
        Settings()  # type: ignore[call-arg]


def test_repository_metrics_valid() -> None:
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
    data = {
        "stargazers_count": "invalid",
        "forks_count": 50,
        "open_issues_count": 10,
    }
    with pytest.raises(ValidationError):
        RepositoryMetrics(**data)  # type: ignore[arg-type]  # type: ignore[arg-type]


def test_commit_item_valid() -> None:
    data = {
        "commit": {
            "author": {
                "name": "Test User",
                "date": "2023-01-01T12:00:00Z",
                "email": "test@example.com",  # Extra field
            },
            "message": "Update README",  # Extra field
        },
        "sha": "abcdef",  # Extra field
    }
    item = CommitItem(**data)  # type: ignore[arg-type]
    assert item.commit.author.name == "Test User"
    assert isinstance(item.commit.author.date, datetime)
    assert item.commit.author.date.year == 2023


def test_commit_item_missing_required() -> None:
    data = {
        "commit": {
            "author": {
                "name": "Test User",
                # missing date
            }
        }
    }
    with pytest.raises(ValidationError):
        CommitItem(**data)  # type: ignore[arg-type]  # type: ignore[arg-type]

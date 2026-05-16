"""Unit tests for the domain models."""

import os
from collections.abc import Generator
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


@pytest.fixture(autouse=True)
def clear_settings_cache() -> Generator[None, None, None]:
    """Ensure the singleton settings cache is cleared before and after each test."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_repository_metrics_valid_data() -> None:
    data: dict[str, object] = {
        "stargazers_count": 100,
        "forks_count": 50,
        "open_issues_count": 10,
        "ignored_extra_field": "test",
    }
    model = RepositoryMetrics(**data)  # type: ignore[arg-type]
    assert model.stargazers_count == 100
    assert model.forks_count == 50
    assert model.open_issues_count == 10
    assert not hasattr(model, "ignored_extra_field")


def test_repository_metrics_invalid_data() -> None:
    data: dict[str, object] = {
        "stargazers_count": "invalid",
        "forks_count": 50,
    }
    with pytest.raises(ValidationError):
        RepositoryMetrics(**data)  # type: ignore[arg-type]


def test_commit_item_valid_data() -> None:
    data: dict[str, object] = {
        "commit": {
            "author": {
                "name": "Jane Doe",
                "date": "2023-10-25T10:00:00Z",
                "extra_author_field": "ignore",
            },
            "extra_commit_field": "ignore",
        },
        "extra_root_field": "ignore",
    }
    model = CommitItem(**data)  # type: ignore[arg-type]
    assert model.commit.author.name == "Jane Doe"
    assert model.commit.author.date == datetime(2023, 10, 25, 10, 0, tzinfo=UTC)
    assert not hasattr(model, "extra_root_field")
    assert not hasattr(model.commit, "extra_commit_field")
    assert not hasattr(model.commit.author, "extra_author_field")


def test_commit_item_invalid_data() -> None:
    data: dict[str, object] = {
        "commit": {
            "author": {
                "date": "2023-10-25T10:00:00Z",
            }
        }
    }
    with pytest.raises(ValidationError):
        CommitItem(**data)  # type: ignore[arg-type]


def test_settings_valid_token() -> None:
    with patch.dict(os.environ, {"GITHUB_TOKEN": "valid_token"}):
        settings = get_settings()
        assert settings.GITHUB_TOKEN == "valid_token" # noqa: S105


def test_settings_missing_token() -> None:
    with patch.dict(os.environ, {}, clear=True), pytest.raises(ValidationError):
        Settings()  # type: ignore[call-arg]

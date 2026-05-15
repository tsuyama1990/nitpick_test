import os
import unittest.mock
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from src.domain_models.config import Settings, get_settings
from src.domain_models.schemas import (
    CommitItem,
    RepositoryMetrics,
)


def test_repository_metrics_valid_data() -> None:
    data = {
        "stargazers_count": 100,
        "forks_count": 50,
        "open_issues_count": 10,
        "extra_field_should_be_stripped": "test",
    }
    metrics = RepositoryMetrics(**data)  # type: ignore[arg-type]
    assert metrics.stargazers_count == 100
    assert metrics.forks_count == 50
    assert metrics.open_issues_count == 10
    assert not hasattr(metrics, "extra_field_should_be_stripped")


def test_repository_metrics_invalid_data() -> None:
    data = {"stargazers_count": "not an int", "forks_count": 50, "open_issues_count": 10}
    with pytest.raises(ValidationError):
        RepositoryMetrics(**data)  # type: ignore[arg-type]


def test_commit_item_valid_data() -> None:
    data = {
        "sha": "12345",
        "commit": {
            "author": {
                "name": "Test User",
                "email": "test@example.com",
                "date": "2023-10-27T10:00:00Z",
            },
            "message": "Initial commit",
        },
    }
    item = CommitItem(**data)  # type: ignore[arg-type]
    assert item.commit.author.name == "Test User"
    assert item.commit.author.date == datetime(2023, 10, 27, 10, 0, tzinfo=UTC)
    assert not hasattr(item.commit.author, "email")
    assert not hasattr(item.commit, "message")
    assert not hasattr(item, "sha")


def test_commit_item_invalid_data_missing_field() -> None:
    data = {"commit": {"author": {"date": "2023-10-27T10:00:00Z"}}}
    with pytest.raises(ValidationError):
        CommitItem(**data)  # type: ignore[arg-type]


def test_settings_valid_token() -> None:
    get_settings.cache_clear()
    with unittest.mock.patch.dict(os.environ, {"GITHUB_TOKEN": "valid_token"}):
        settings = Settings()  # type: ignore[call-arg]
        assert settings.GITHUB_TOKEN == "valid_token"  # noqa: S105


def test_settings_missing_token() -> None:
    get_settings.cache_clear()
    env = os.environ.copy()
    if "GITHUB_TOKEN" in env:
        del env["GITHUB_TOKEN"]

    with unittest.mock.patch.dict(os.environ, env, clear=True), pytest.raises(ValidationError):
        Settings()  # type: ignore[call-arg]


def test_get_settings_caching() -> None:
    get_settings.cache_clear()
    with unittest.mock.patch.dict(os.environ, {"GITHUB_TOKEN": "token1"}):
        s1 = get_settings()

    with unittest.mock.patch.dict(os.environ, {"GITHUB_TOKEN": "token2"}):
        s2 = get_settings()

    assert s1 is s2
    assert s1.GITHUB_TOKEN == "token1"  # noqa: S105
    assert s2.GITHUB_TOKEN == "token1"  # noqa: S105

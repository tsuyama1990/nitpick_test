import os
import unittest.mock
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from src.config import Settings, get_settings
from src.domain_models.schemas import CommitItem, RepositoryMetrics


def test_repository_metrics_valid() -> None:
    data: dict[str, object] = {
        "stargazers_count": 10,
        "forks_count": 5,
        "open_issues_count": 2,
        "unknown_field": "ignore",
    }
    model = RepositoryMetrics(**data)  # type: ignore[arg-type]
    assert model.stargazers_count == 10
    assert model.forks_count == 5
    assert model.open_issues_count == 2
    assert not hasattr(model, "unknown_field")


def test_repository_metrics_invalid() -> None:
    data: dict[str, object] = {"stargazers_count": "not_an_int", "forks_count": 5, "open_issues_count": 2}
    with pytest.raises(ValidationError):
        RepositoryMetrics(**data)  # type: ignore[arg-type]


def test_commit_item_valid() -> None:
    data: dict[str, object] = {
        "commit": {
            "author": {
                "name": "Test User",
                "date": "2023-01-01T12:00:00Z",
                "email": "test@example.com",
            },
            "message": "Initial commit",
        },
        "sha": "123456",
    }
    model = CommitItem(**data)  # type: ignore[arg-type]
    assert model.commit.author.name == "Test User"
    assert isinstance(model.commit.author.date, datetime)
    assert model.commit.author.date == datetime(2023, 1, 1, 12, 0, tzinfo=UTC)


def test_commit_item_invalid() -> None:
    data: dict[str, object] = {
        "commit": {
            "author": {
                # missing name
                "date": "2023-01-01T12:00:00Z"
            }
        }
    }
    with pytest.raises(ValidationError):
        CommitItem(**data)  # type: ignore[arg-type]


def test_settings_load_success() -> None:
    get_settings.cache_clear()
    with unittest.mock.patch.dict(os.environ, {"GITHUB_TOKEN": "dummy_token"}):
        settings = Settings()  # type: ignore[call-arg]
        assert settings.GITHUB_TOKEN == "dummy_token"  # noqa: S105


def test_settings_load_failure() -> None:
    get_settings.cache_clear()
    with unittest.mock.patch.dict(os.environ, clear=True), pytest.raises(ValidationError):
        Settings()  # type: ignore[call-arg]

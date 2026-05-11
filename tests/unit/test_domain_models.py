import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from src.domain_models import (
    CommitAuthor,
    CommitItem,
    RepositoryMetrics,
    Settings,
    get_settings,
)


def test_repository_metrics_valid() -> None:
    model = RepositoryMetrics(stargazers_count=100, forks_count=50, open_issues_count=10)
    assert model.stargazers_count == 100
    assert model.forks_count == 50
    assert model.open_issues_count == 10


def test_repository_metrics_invalid_type() -> None:
    data = {"stargazers_count": "one", "forks_count": 50, "open_issues_count": 10}
    with pytest.raises(ValidationError):
        RepositoryMetrics(**data)  # type: ignore[arg-type]


def test_repository_metrics_extra_fields() -> None:
    data = {"stargazers_count": 100, "forks_count": 50, "open_issues_count": 10, "extra": "invalid"}
    with pytest.raises(ValidationError):
        RepositoryMetrics(**data)  # type: ignore[arg-type]


def test_commit_author_valid() -> None:
    data = {"name": "Test User", "date": "2024-01-01T12:00:00Z"}
    model = CommitAuthor(**data)  # type: ignore[arg-type]
    assert model.name == "Test User"
    assert model.date.isoformat() == "2024-01-01T12:00:00+00:00"


def test_commit_item_valid() -> None:
    data = {"commit": {"author": {"name": "Test User", "date": "2024-01-01T12:00:00Z"}}}
    model = CommitItem(**data)  # type: ignore[arg-type]
    assert model.commit.author.name == "Test User"


@pytest.fixture(autouse=True)
def clear_settings_cache() -> None:
    """Clear the lru_cache for settings between tests."""
    import functools

    if isinstance(get_settings, functools._lru_cache_wrapper):
        get_settings.cache_clear()


def test_settings_valid() -> None:
    with patch.dict(
        os.environ, {"GITHUB_TOKEN": "test_token", "ENV_FILE": ".env.test"}, clear=True
    ):
        settings = Settings()  # type: ignore[call-arg]
        assert settings.GITHUB_TOKEN == "test_token"


def test_settings_missing_token() -> None:

    with (
        patch.dict(os.environ, {"ENV_FILE": ".env.test"}, clear=True),
        pytest.raises(ValidationError),
    ):
        Settings()  # type: ignore[call-arg]

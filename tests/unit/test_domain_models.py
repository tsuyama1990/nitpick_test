from typing import Any

import pytest
from pydantic import ValidationError

from src.domain_models.github import Commit, RepositoryMetrics


def test_repository_metrics_parsing() -> None:
    data: dict[str, Any] = {
        "stargazers_count": 100,
        "forks_count": 50,
        "open_issues_count": 10,
    }
    metrics = RepositoryMetrics(**data)
    assert metrics.stargazers_count == 100
    assert metrics.forks_count == 50
    assert metrics.open_issues_count == 10


def test_repository_metrics_extra_fields_forbidden() -> None:
    data: dict[str, Any] = {
        "stargazers_count": 100,
        "forks_count": 50,
        "open_issues_count": 10,
        "extra_unwanted_key": 999,
    }
    with pytest.raises(ValidationError):
        RepositoryMetrics(**data)


def test_repository_metrics_missing_fields() -> None:
    with pytest.raises(ValidationError):
        RepositoryMetrics(stargazers_count=100)  # type: ignore


def test_commit_parsing_flat() -> None:
    data: dict[str, Any] = {"name": "Bob", "date": "2023-01-02T12:00:00Z"}
    commit = Commit(**data)
    assert commit.name == "Bob"


def test_commit_extra_fields_forbidden() -> None:
    data: dict[str, Any] = {
        "name": "Bob",
        "date": "2023-01-02T12:00:00Z",
        "extra_bad_field": "test",
    }
    with pytest.raises(ValidationError):
        Commit(**data)


def test_commit_missing_fields() -> None:
    with pytest.raises(ValidationError):
        Commit(name="test")  # type: ignore

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from src.domain_models.schemas import Commit, CommitAuthor, CommitInfo, RepositoryMetrics


def test_repository_metrics_valid() -> None:
    metrics = RepositoryMetrics(stargazers_count=100, forks_count=50, open_issues_count=10)
    assert metrics.stargazers_count == 100


def test_repository_metrics_invalid() -> None:
    with pytest.raises(ValidationError):
        RepositoryMetrics(stargazers_count=-1, forks_count=50, open_issues_count=10)


def test_repository_metrics_extra_forbid() -> None:
    with pytest.raises(ValidationError):
        RepositoryMetrics(stargazers_count=100, forks_count=50, open_issues_count=10, extra="field")  # type: ignore[call-arg]


def test_commit_schema() -> None:
    now = datetime.now(UTC)
    commit = Commit(
        sha="abc",
        commit=CommitInfo(author=CommitAuthor(name="test", date=now), message="Test commit"),
    )
    assert commit.sha == "abc"
    assert commit.commit.author.name == "test"

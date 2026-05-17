from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from src.domain_models.config import Settings
from src.domain_models.schemas import CommitAuthor, CommitData, CommitItem, RepositoryMetrics


def test_repository_metrics_valid() -> None:
    data = {"stargazers_count": 100, "forks_count": 50, "open_issues_count": 5}
    metrics = RepositoryMetrics(
        stargazers_count=data["stargazers_count"],
        forks_count=data["forks_count"],
        open_issues_count=data["open_issues_count"],
    )
    assert metrics.stargazers_count == 100


def test_repository_metrics_extra_forbid() -> None:
    with pytest.raises(ValidationError):
        RepositoryMetrics(
            stargazers_count=100,
            forks_count=50,
            open_issues_count=5,
            extra_field="should fail",  # type: ignore[call-arg]
        )


def test_commit_item_valid() -> None:
    author = CommitAuthor(name="Alice", date=datetime(2023, 1, 1, 10, 0, 0, tzinfo=UTC))
    data = CommitData(author=author)
    item = CommitItem(commit=data)
    assert item.commit.author.name == "Alice"


def test_settings_missing_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    with pytest.raises(ValidationError):
        Settings()  # type: ignore[call-arg]


def test_settings_valid_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "fake_token")
    settings = Settings(GITHUB_TOKEN="fake_token")  # noqa: S106
    assert settings.github_token == "fake_token"  # noqa: S105

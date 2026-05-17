import datetime

import pytest
from pydantic import ValidationError

from src.domain_models.schemas import CommitAuthor, CommitData, CommitItem, RepositoryMetrics


def test_repository_metrics_valid() -> None:
    data = {
        "stargazers_count": 100,
        "forks_count": 50,
        "open_issues_count": 10,
    }
    metrics = RepositoryMetrics(
        stargazers_count=int(data["stargazers_count"]),
        forks_count=int(data["forks_count"]),
        open_issues_count=int(data["open_issues_count"]),
    )
    assert metrics.stargazers_count == 100
    assert metrics.forks_count == 50
    assert metrics.open_issues_count == 10


def test_repository_metrics_invalid() -> None:
    data = {
        "stargazers_count": 100,
        "forks_count": 50,
        "open_issues_count": 10,
        "extra_field": "invalid",
    }
    with pytest.raises(ValidationError):
        RepositoryMetrics(**data)  # type: ignore[arg-type]


def test_commit_item_valid() -> None:
    date_str = "2023-10-27T10:00:00Z"
    data = {
        "commit": {
            "author": {
                "name": "Alice",
                "date": date_str,
            }
        }
    }
    author_data = data["commit"]["author"]
    author = CommitAuthor(
        name=str(author_data["name"]),
        date=datetime.datetime.fromisoformat(str(author_data["date"]).replace("Z", "+00:00")),
    )
    commit_data = CommitData(author=author)
    item = CommitItem(commit=commit_data)

    assert item.commit.author.name == "Alice"


def test_commit_item_invalid() -> None:
    data = {
        "commit": {
            "author": {
                "name": "Alice",
                # missing date
            }
        }
    }
    author_data = data["commit"]["author"]
    with pytest.raises(ValidationError):
        CommitAuthor(**author_data)  # type: ignore[arg-type]

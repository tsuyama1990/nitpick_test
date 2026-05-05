from datetime import UTC, datetime

import polars as pl
import pytest
from pydantic import ValidationError

from src.domain_models.dashboard import DashboardData
from src.domain_models.github import CommitRecord, RepoMetadata


def test_repo_metadata_valid() -> None:
    model = RepoMetadata(stargazers_count=10, forks_count=5, open_issues_count=2)
    assert model.stargazers_count == 10


def test_repo_metadata_invalid_negative() -> None:
    with pytest.raises(ValidationError):
        RepoMetadata(stargazers_count=-1, forks_count=5, open_issues_count=2)


def test_commit_record_valid() -> None:
    dt = datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC)
    model = CommitRecord(date=dt, author_name="Alice", message="Init")
    assert model.author_name == "Alice"
    assert model.date == dt


def test_commit_record_invalid_empty_author() -> None:
    with pytest.raises(ValidationError):
        CommitRecord(
            date=datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC), author_name="", message="Init"
        )


def test_dashboard_data_valid() -> None:
    meta = RepoMetadata(stargazers_count=10, forks_count=5, open_issues_count=2)
    daily_df = pl.DataFrame({"date": [], "commit_count": []})
    top_df = pl.DataFrame({"author_name": [], "commit_count": []})

    model = DashboardData(repo_metadata=meta, daily_commits_df=daily_df, top_committers_df=top_df)
    assert model.repo_metadata.stargazers_count == 10
    assert len(model.daily_commits_df) == 0


def test_dashboard_data_extra_forbid() -> None:
    meta = RepoMetadata(stargazers_count=10, forks_count=5, open_issues_count=2)
    daily_df = pl.DataFrame({"date": [], "commit_count": []})
    top_df = pl.DataFrame({"author_name": [], "commit_count": []})

    with pytest.raises(ValidationError):
        DashboardData(
            repo_metadata=meta,
            daily_commits_df=daily_df,
            top_committers_df=top_df,
            unknown_field=True,  # type: ignore[call-arg]
        )

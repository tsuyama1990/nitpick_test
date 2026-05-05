from datetime import UTC, datetime

import polars as pl

from src.domain_models.github import CommitRecord
from src.processing.transformer import (
    transform_commits_to_daily_trends,
    transform_commits_to_top_committers,
)


def test_transform_commits_to_daily_trends() -> None:
    commits = [
        CommitRecord(date=datetime(2023, 1, 1, 10, 0, 0, tzinfo=UTC), author_name="A", message="m"),
        CommitRecord(date=datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC), author_name="B", message="m"),
        CommitRecord(date=datetime(2023, 1, 2, 10, 0, 0, tzinfo=UTC), author_name="A", message="m"),
    ]
    df = transform_commits_to_daily_trends(commits)
    assert len(df) == 2
    assert df.filter(pl.col("date") == datetime(2023, 1, 1, tzinfo=UTC).date())["commit_count"][0] == 2
    assert df.filter(pl.col("date") == datetime(2023, 1, 2, tzinfo=UTC).date())["commit_count"][0] == 1

def test_transform_commits_empty() -> None:
    df1 = transform_commits_to_daily_trends([])
    assert len(df1) == 0
    df2 = transform_commits_to_top_committers([])
    assert len(df2) == 0

def test_transform_commits_to_top_committers() -> None:
    commits = [
        CommitRecord(date=datetime(2023, 1, 1, 10, 0, 0, tzinfo=UTC), author_name="A", message="m"),
        CommitRecord(date=datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC), author_name="A", message="m"),
        CommitRecord(date=datetime(2023, 1, 2, 10, 0, 0, tzinfo=UTC), author_name="B", message="m"),
    ]
    df = transform_commits_to_top_committers(commits)
    assert len(df) == 2
    assert df[0]["author_name"][0] == "A"
    assert df[0]["commit_count"][0] == 2

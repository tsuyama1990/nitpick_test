from datetime import UTC, datetime

import polars as pl

from src.domain_models import CommitRecord
from src.processing.transformer import calculate_daily_commits, get_top_committers


def test_calculate_daily_commits() -> None:
    records = [
        CommitRecord(
            commit_hash="a1", author="alice", date=datetime(2023, 1, 1, 10, 0, tzinfo=UTC)
        ),
        CommitRecord(
            commit_hash="a2", author="alice", date=datetime(2023, 1, 1, 12, 0, tzinfo=UTC)
        ),
        CommitRecord(commit_hash="b1", author="bob", date=datetime(2023, 1, 2, 10, 0, tzinfo=UTC)),
    ]
    df = calculate_daily_commits(records)

    assert isinstance(df, pl.DataFrame)
    assert df.columns == ["date", "commit_count"]

    res = df.to_dicts()
    assert len(res) == 2
    # Verify exact calculations
    counts = {row["date"]: row["commit_count"] for row in res}
    assert counts["2023-01-01"] == 2
    assert counts["2023-01-02"] == 1


def test_get_top_committers() -> None:
    records = [
        CommitRecord(commit_hash="a1", author="alice", date=datetime(2023, 1, 1, tzinfo=UTC)),
        CommitRecord(commit_hash="a2", author="alice", date=datetime(2023, 1, 2, tzinfo=UTC)),
        CommitRecord(commit_hash="a3", author="alice", date=datetime(2023, 1, 3, tzinfo=UTC)),
        CommitRecord(commit_hash="b1", author="bob", date=datetime(2023, 1, 1, tzinfo=UTC)),
        CommitRecord(commit_hash="b2", author="bob", date=datetime(2023, 1, 2, tzinfo=UTC)),
        CommitRecord(commit_hash="c1", author="charlie", date=datetime(2023, 1, 1, tzinfo=UTC)),
        CommitRecord(commit_hash="d1", author="dave", date=datetime(2023, 1, 1, tzinfo=UTC)),
        CommitRecord(commit_hash="e1", author="eve", date=datetime(2023, 1, 1, tzinfo=UTC)),
        CommitRecord(commit_hash="f1", author="frank", date=datetime(2023, 1, 1, tzinfo=UTC)),
    ]
    df = get_top_committers(records)

    assert isinstance(df, pl.DataFrame)
    assert df.columns == ["author", "commit_count"]

    res = df.to_dicts()
    assert len(res) == 5
    assert res[0]["author"] == "alice"
    assert res[0]["commit_count"] == 3
    assert res[1]["author"] == "bob"
    assert res[1]["commit_count"] == 2

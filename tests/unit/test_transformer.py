import sys
from pathlib import Path

# Fix module imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from datetime import UTC, date, datetime

import polars as pl

from src.domain_models import CommitRecord
from src.transformer import aggregate_commits_by_date, get_top_committers


def test_aggregate_commits_by_date() -> None:
    records = [
        CommitRecord(sha="1", author="alice", date=datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC)),
        CommitRecord(sha="2", author="bob", date=datetime(2023, 1, 1, 14, 0, 0, tzinfo=UTC)),
        CommitRecord(sha="3", author="alice", date=datetime(2023, 1, 2, 12, 0, 0, tzinfo=UTC)),
        CommitRecord(sha="4", author="alice", date=date(2023, 1, 2)),
    ]

    df = aggregate_commits_by_date(records)

    assert df.columns == ["date", "commit_count"]
    assert len(df) == 2

    # Check correct aggregation
    row1 = df.filter(pl.col("date") == date(2023, 1, 1)).row(0)
    assert row1[1] == 2

    row2 = df.filter(pl.col("date") == date(2023, 1, 2)).row(0)
    assert row2[1] == 2


def test_get_top_committers() -> None:
    records = [
        CommitRecord(sha="1", author="alice", date=datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC)),
        CommitRecord(sha="2", author="bob", date=datetime(2023, 1, 1, 14, 0, 0, tzinfo=UTC)),
        CommitRecord(sha="3", author="alice", date=datetime(2023, 1, 2, 12, 0, 0, tzinfo=UTC)),
        CommitRecord(sha="4", author="charlie", date=date(2023, 1, 2)),
        CommitRecord(sha="5", author="dave", date=date(2023, 1, 2)),
        CommitRecord(sha="6", author="eve", date=date(2023, 1, 2)),
        CommitRecord(sha="7", author="frank", date=date(2023, 1, 2)),
        CommitRecord(sha="8", author="alice", date=date(2023, 1, 3)),
    ]

    df = get_top_committers(records)

    assert df.columns == ["author", "commit_count"]
    assert len(df) == 5  # Top 5

    # Check correct sorting
    assert df.row(0) == ("alice", 3)

    authors = df.get_column("author").to_list()
    assert "alice" in authors
    assert (
        "frank" not in authors
    )  # frank should be out of top 5 or tie break depends on logic but alice is definitely 1

from datetime import UTC, datetime

import polars as pl
import pytest
from src.domain_models import CommitRecord
from src.processing.transformer import calculate_daily_commits, get_top_committers


def test_calculate_daily_commits() -> None:
    records = [
        CommitRecord(commit_hash="1", author="a", date=datetime(2023, 1, 1, 10, tzinfo=UTC)),
        CommitRecord(commit_hash="2", author="b", date=datetime(2023, 1, 1, 12, tzinfo=UTC)),
        CommitRecord(commit_hash="3", author="a", date=datetime(2023, 1, 2, 10, tzinfo=UTC)),
    ]
    df = calculate_daily_commits(records)
    assert len(df) == 2
    assert "date" in df.columns
    assert "commit_count" in df.columns

    # Check empty
    df_empty = calculate_daily_commits([])
    assert len(df_empty) == 0


def test_get_top_committers() -> None:
    records = [
        CommitRecord(commit_hash="1", author="alice", date=datetime(2023, 1, 1, tzinfo=UTC)),
        CommitRecord(commit_hash="2", author="alice", date=datetime(2023, 1, 1, tzinfo=UTC)),
        CommitRecord(commit_hash="3", author="bob", date=datetime(2023, 1, 1, tzinfo=UTC)),
    ]
    df = get_top_committers(records)
    assert len(df) == 2
    assert df.row(0) == ("alice", 2)
    assert df.row(1) == ("bob", 1)

    df_empty = get_top_committers([])
    assert len(df_empty) == 0

def test_records_to_df_empty() -> None:
    from src.processing.transformer import _records_to_df
    df = _records_to_df([])
    assert len(df) == 0

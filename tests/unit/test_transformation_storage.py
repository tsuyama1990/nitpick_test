import datetime
import os
import pathlib
import time

import polars as pl
import pytest

from src.domain_models.github import CommitAuthor, CommitDetail, CommitInfo
from src.storage import _is_cache_valid, load_cached_dataframe, save_dataframe_to_cache
from src.transformation import aggregate_commits_by_author, aggregate_commits_by_date


def test_aggregate_commits_by_date() -> None:
    commits = [
        CommitInfo(commit=CommitDetail(author=CommitAuthor(name="A", date="2023-01-01T10:00:00Z"))),
        CommitInfo(commit=CommitDetail(author=CommitAuthor(name="B", date="2023-01-01T12:00:00Z"))),
        CommitInfo(commit=CommitDetail(author=CommitAuthor(name="C", date="2023-01-02T10:00:00Z"))),
    ]

    df = aggregate_commits_by_date(commits)

    assert len(df) == 2
    assert df.columns == ["date", "commit_count"]

    # Check data
    date_2023_01_01 = datetime.date(2023, 1, 1)
    date_2023_01_02 = datetime.date(2023, 1, 2)

    assert df.filter(pl.col("date") == date_2023_01_01)["commit_count"][0] == 2
    assert df.filter(pl.col("date") == date_2023_01_02)["commit_count"][0] == 1


def test_aggregate_commits_by_author() -> None:
    commits = [
        CommitInfo(
            commit=CommitDetail(author=CommitAuthor(name="Alice", date="2023-01-01T10:00:00Z"))
        ),
        CommitInfo(
            commit=CommitDetail(author=CommitAuthor(name="Bob", date="2023-01-01T12:00:00Z"))
        ),
        CommitInfo(
            commit=CommitDetail(author=CommitAuthor(name="Alice", date="2023-01-02T10:00:00Z"))
        ),
        CommitInfo(
            commit=CommitDetail(author=CommitAuthor(name="Charlie", date="2023-01-02T10:00:00Z"))
        ),
        CommitInfo(
            commit=CommitDetail(author=CommitAuthor(name="Alice", date="2023-01-03T10:00:00Z"))
        ),
        CommitInfo(
            commit=CommitDetail(author=CommitAuthor(name="David", date="2023-01-03T10:00:00Z"))
        ),
        CommitInfo(
            commit=CommitDetail(author=CommitAuthor(name="Eve", date="2023-01-03T10:00:00Z"))
        ),
        CommitInfo(
            commit=CommitDetail(author=CommitAuthor(name="Frank", date="2023-01-03T10:00:00Z"))
        ),
    ]

    df = aggregate_commits_by_author(commits)

    assert len(df) == 5
    assert df.columns == ["author", "commit_count"]

    # Alice should be first with 3 commits
    assert df["author"][0] == "Alice"
    assert df["commit_count"][0] == 3


def test_aggregate_empty_commits() -> None:
    df_date = aggregate_commits_by_date([])
    assert len(df_date) == 0
    assert df_date.columns == ["date", "commit_count"]

    df_author = aggregate_commits_by_author([])
    assert len(df_author) == 0
    assert df_author.columns == ["author", "commit_count"]


def test_cache_logic(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CACHE_DIR", str(tmp_path))

    df = pl.DataFrame({"a": [1, 2, 3]})
    cache_key = "test_cache"

    # Test miss
    miss = load_cached_dataframe(cache_key)
    assert miss is None

    # Save cache
    save_dataframe_to_cache(df, cache_key)

    # Test hit
    hit = load_cached_dataframe(cache_key)
    assert hit is not None
    assert hit.equals(df)

    # Test TTL logic specifically
    filepath = tmp_path / f"{cache_key}.parquet"

    # Valid TTL
    assert _is_cache_valid(filepath, ttl_seconds=3600) is True

    # Expired TTL
    # Set modify time to 2 hours ago
    past_time = time.time() - 7200
    os.utime(filepath, (past_time, past_time))

    assert _is_cache_valid(filepath, ttl_seconds=3600) is False

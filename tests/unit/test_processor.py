import pathlib
import time
from unittest.mock import patch

import polars as pl

from src.domain_models.github import CommitInfo
from src.transformation.processor import (
    aggregate_commits_per_day,
    get_top_committers,
    load_from_cache,
    save_to_cache,
)


def test_aggregate_commits_per_day() -> None:
    commits = [
        CommitInfo(commit={"author": {"date": "2023-10-27T10:00:00Z", "name": "User1"}}), # type: ignore[call-arg]
        CommitInfo(commit={"author": {"date": "2023-10-27T11:00:00Z", "name": "User2"}}), # type: ignore[call-arg]
        CommitInfo(commit={"author": {"date": "2023-10-28T10:00:00Z", "name": "User1"}}), # type: ignore[call-arg]
    ]
    df = aggregate_commits_per_day(commits)

    assert isinstance(df, pl.DataFrame)
    assert len(df) == 2
    row1 = df.filter(pl.col("date") == "2023-10-27").row(0)
    assert row1[1] == 2

def test_get_top_committers() -> None:
    commits = [
        CommitInfo(commit={"author": {"date": "2023-10-27T10:00:00Z", "name": "User1"}}), # type: ignore[call-arg]
        CommitInfo(commit={"author": {"date": "2023-10-27T11:00:00Z", "name": "User1"}}), # type: ignore[call-arg]
        CommitInfo(commit={"author": {"date": "2023-10-28T10:00:00Z", "name": "User2"}}), # type: ignore[call-arg]
        CommitInfo(commit={"author": {"date": "2023-10-28T10:00:00Z", "name": "User3"}}), # type: ignore[call-arg]
        CommitInfo(commit={"author": {"date": "2023-10-28T10:00:00Z", "name": "User4"}}), # type: ignore[call-arg]
        CommitInfo(commit={"author": {"date": "2023-10-28T10:00:00Z", "name": "User5"}}), # type: ignore[call-arg]
        CommitInfo(commit={"author": {"date": "2023-10-28T10:00:00Z", "name": "User6"}}), # type: ignore[call-arg]
    ]
    df = get_top_committers(commits)

    assert len(df) == 5
    assert df.row(0)[0] == "User1"
    assert df.row(0)[1] == 2

def test_cache_logic(tmp_path: pathlib.Path) -> None:
    with patch.dict("os.environ", {"CACHE_DIR": str(tmp_path)}):
        df = pl.DataFrame({"a": [1, 2, 3]})
        save_to_cache(df, "test.parquet")

        loaded = load_from_cache("test.parquet")
        assert loaded is not None
        assert loaded.equals(df)

        assert load_from_cache("not_exist.parquet") is None

        # Test TTL
        with patch("time.time", return_value=time.time() + 4000):
            assert load_from_cache("test.parquet", ttl_seconds=3600) is None

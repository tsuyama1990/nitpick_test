import os
import time
from pathlib import Path

import polars as pl

from src.processing.cache import LocalCache


def test_uat_c04_01_cache_hit_accuracy(tmp_path: Path) -> None:
    # GIVEN a pre-calculated Polars DataFrame representing aggregated commit data
    df = pl.DataFrame({"date": ["2023-01-01", "2023-01-02"], "commits": [10, 15]})

    cache = LocalCache(cache_dir=tmp_path)

    # WHEN the DataFrame is saved to the cache and immediately retrieved
    cache.set("aggregated_commits", df)
    retrieved_df = cache.get("aggregated_commits")

    # THEN the retrieved DataFrame must be structurally identical to the original DataFrame
    # AND all column data types must be perfectly preserved after the Parquet serialization round-trip.
    assert retrieved_df is not None
    assert retrieved_df.equals(df)
    assert retrieved_df.dtypes == df.dtypes


def test_uat_c04_02_ttl_expiration_logic(tmp_path: Path) -> None:
    # GIVEN a cached Parquet file containing historical commit data
    df = pl.DataFrame({"date": ["2023-01-01"], "commits": [10]})

    ttl = 3600  # 1-hour TTL
    cache = LocalCache(cache_dir=tmp_path, ttl_seconds=ttl)
    cache.set("historical_commits", df)

    path = tmp_path / "historical_commits.parquet"

    # AND the file's metadata indicates it was created 2 hours ago
    two_hours_ago = time.time() - 7200
    os.utime(path, (two_hours_ago, two_hours_ago))

    # WHEN the system attempts to retrieve the data from a cache configured with a 1-hour TTL
    retrieved_df = cache.get("historical_commits")

    # THEN the cache must report a cache miss (return None)
    # AND signal to the upstream orchestrator that fresh data must be ingested from the external API.
    assert retrieved_df is None

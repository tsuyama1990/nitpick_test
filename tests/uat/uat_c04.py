import os
import time
from pathlib import Path

import polars as pl
from src.processing.cache import LocalCache


def test_uat_c04_01_cache_hit_accuracy(tmp_path: Path) -> None:
    """
    Scenario ID: UAT-C04-01
    Description: Verify the local caching system successfully serializes and deserializes
    Polars DataFrames without data loss or schema alteration.
    """
    cache = LocalCache(cache_dir=tmp_path, ttl_seconds=3600)

    # GIVEN a pre-calculated Polars DataFrame representing aggregated commit data
    df = pl.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "commits": [10, 20, 15],
            "author": ["Alice", "Bob", "Alice"],
        }
    )

    # WHEN the DataFrame is saved to the cache and immediately retrieved
    cache.set("aggregated_commit_data", df)
    retrieved_df = cache.get("aggregated_commit_data")

    # THEN the retrieved DataFrame must be structurally identical to the original DataFrame
    assert retrieved_df is not None
    assert df.equals(retrieved_df)

    # AND all column data types must be perfectly preserved after the Parquet serialization round-trip
    assert df.schema == retrieved_df.schema


def test_uat_c04_02_ttl_expiration_logic(tmp_path: Path) -> None:
    """
    Scenario ID: UAT-C04-02
    Description: Verify the caching system correctly invalidates stale data based on the Time-To-Live (TTL) configuration.
    """
    # GIVEN a cached Parquet file containing historical commit data
    cache = LocalCache(cache_dir=tmp_path, ttl_seconds=3600)  # 1-hour TTL
    df = pl.DataFrame({"data": [1, 2, 3]})
    cache.set("historical_commits", df)

    # AND the file's metadata indicates it was created 2 hours ago
    file_path = tmp_path / "historical_commits.parquet"
    two_hours_ago = time.time() - 7200
    os.utime(file_path, (two_hours_ago, two_hours_ago))

    # WHEN the system attempts to retrieve the data from a cache configured with a 1-hour TTL
    retrieved_df = cache.get("historical_commits")

    # THEN the cache must report a cache miss (return None)
    assert retrieved_df is None

import os
import time
from pathlib import Path

import polars as pl

from src.processing.cache import LocalCache


def test_uat_c04_01_serialization_accuracy(tmp_path: Path) -> None:
    """
    Scenario ID: UAT-C04-01
    Verify the local caching system successfully serializes and deserializes
    Polars DataFrames without data loss or schema alteration.
    """
    # GIVEN a pre-calculated Polars DataFrame representing aggregated commit data
    cache = LocalCache(cache_dir=tmp_path)
    df = pl.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "commits": [15, 2, 42],
            "author": ["alice", "bob", "alice"],
        }
    )

    # WHEN the DataFrame is saved to the cache and immediately retrieved
    key = "uat_c04_01"
    cache.set(key, df)
    retrieved_df = cache.get(key)

    # THEN the retrieved DataFrame must be structurally identical to the original DataFrame
    # AND all column data types must be perfectly preserved
    assert retrieved_df is not None
    assert df.equals(retrieved_df), "Retrieved DataFrame does not match the original."
    assert df.schema == retrieved_df.schema, (
        "Schema was altered during serialization/deserialization."
    )


def test_uat_c04_02_ttl_expiration_logic(tmp_path: Path) -> None:
    """
    Scenario ID: UAT-C04-02
    Verify the caching system correctly invalidates stale data based on TTL.
    """
    # GIVEN a cached Parquet file containing historical commit data
    # AND the file's metadata indicates it was created 2 hours ago
    ttl_seconds = 3600  # 1 hour
    cache = LocalCache(cache_dir=tmp_path, ttl_seconds=ttl_seconds)

    df = pl.DataFrame({"metric": [100]})
    key = "uat_c04_02"
    cache.set(key, df)

    # Artificially age the file
    file_path = tmp_path / f"{key}.parquet"
    current_time = time.time()
    past_time = current_time - 7200  # 2 hours ago
    os.utime(file_path, (current_time, past_time))

    # WHEN the system attempts to retrieve the data from a cache configured with a 1-hour TTL
    retrieved_df = cache.get(key)

    # THEN the cache must report a cache miss (return None)
    assert retrieved_df is None, "Cache should have reported a miss due to TTL expiration."

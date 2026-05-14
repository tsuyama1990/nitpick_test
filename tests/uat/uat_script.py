import os
import shutil
import time
from pathlib import Path

import polars as pl

from src.processing.cache import LocalCache


def run_uat() -> None:
    print("Starting UAT for Cycle 04: Local Caching Implementation...")  # noqa: T201

    # Use a specific directory for UAT to act as a realistic cache dir, then clean up.
    cache_dir = Path(".uat_cache")
    if cache_dir.exists():
        shutil.rmtree(cache_dir)

    cache = LocalCache(cache_dir=cache_dir, ttl_seconds=3600)

    print("\n--- Running Scenario UAT-C04-01: Cache Hit Accuracy ---")  # noqa: T201
    df = pl.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "commits": [10, 20, 15],
            "author": ["alice", "bob", "alice"],
        }
    )

    cache.set("uat_test_data", df)
    retrieved_df = cache.get("uat_test_data")

    assert retrieved_df is not None, "Cache Hit Accuracy Failed: retrieved_df is None"
    assert retrieved_df.equals(df), "Cache Hit Accuracy Failed: DataFrames do not match"
    print("✓ Scenario UAT-C04-01 Passed: Retrieved DataFrame is identical to the original.")  # noqa: T201

    print("\n--- Running Scenario UAT-C04-02: TTL Expiration Logic ---")  # noqa: T201
    # Save another file
    cache.set("uat_test_ttl", df)

    # Backdate to simulate it was created 2 hours ago
    file_path = cache_dir / "uat_test_ttl.parquet"
    past_time = time.time() - 7200
    os.utime(file_path, (past_time, past_time))

    # Attempt retrieval
    miss_df = cache.get("uat_test_ttl")
    assert miss_df is None, "TTL Expiration Logic Failed: DataFrame was retrieved instead of None"
    print("✓ Scenario UAT-C04-02 Passed: Stale cache was correctly invalidated and returned None.")  # noqa: T201

    print("\nAll UAT scenarios passed successfully.")  # noqa: T201

    # Clean up
    if cache_dir.exists():
        shutil.rmtree(cache_dir)


if __name__ == "__main__":
    run_uat()

import os
import sys
import time
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).parent.parent.parent.resolve()))
from src.processing.cache import LocalCache


def run_uat() -> None:
    print(  # noqa: T201
    "Starting UAT for Local Caching Implementation (Cycle 04)...")

    # Setup test directory and dummy data
    test_dir = Path("uat_cache_dir")
    cache = LocalCache(cache_dir=test_dir, ttl_seconds=2)

    dummy_df = pl.DataFrame({
        "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
        "commits": [10, 15, 20],
        "author": ["Alice", "Bob", "Alice"]
    })

    print(  # noqa: T201
    "\n--- UAT-C04-01: Cache Hit Accuracy ---")
    print(  # noqa: T201
    "GIVEN a pre-calculated Polars DataFrame representing aggregated commit data")
    print(  # noqa: T201
    "WHEN the DataFrame is saved to the cache and immediately retrieved")

    cache.set("uat_test_data", dummy_df)
    retrieved_df = cache.get("uat_test_data")

    assert retrieved_df is not None, "Cache failed to retrieve data"
    assert isinstance(retrieved_df, pl.DataFrame), "Retrieved data is not a Polars DataFrame"

    # Assert structural equality
    assert retrieved_df.equals(dummy_df), "Retrieved DataFrame structure or data does not match original"

    # Assert schema types match exactly
    assert retrieved_df.schema == dummy_df.schema, "DataFrame schema types altered during round-trip"

    print(  # noqa: T201
    "THEN the retrieved DataFrame is structurally identical to the original DataFrame")
    print(  # noqa: T201
    "AND all column data types are perfectly preserved.")
    print(  # noqa: T201
    "✓ UAT-C04-01 Passed")

    print(  # noqa: T201
    "\n--- UAT-C04-02: TTL Expiration Logic ---")
    print(  # noqa: T201
    "GIVEN a cached Parquet file containing historical commit data")

    file_path = test_dir / "uat_test_data.parquet"
    assert file_path.exists(), "Cache file missing for UAT-C04-02"

    print(  # noqa: T201
    "AND the file's metadata indicates it was created past the TTL (Simulating 2 hours ago for 1-hour TTL)")
    # Manipulate metadata to simulate expiration (backdate by TTL + 10s)
    current_time = time.time()
    past_time = current_time - (cache.ttl_seconds + 10)
    os.utime(file_path, (past_time, past_time))

    print(  # noqa: T201
    "WHEN the system attempts to retrieve the data from a cache configured with a strict TTL")
    expired_retrieval = cache.get("uat_test_data")

    assert expired_retrieval is None, "Cache incorrectly returned stale data instead of None"

    print(  # noqa: T201
    "THEN the cache reports a cache miss (returns None)")
    print(  # noqa: T201
    "AND signals to the upstream orchestrator that fresh data must be ingested.")
    print(  # noqa: T201
    "✓ UAT-C04-02 Passed")

    print(  # noqa: T201
    "\nCleaning up UAT artifacts...")
    if file_path.exists():
        file_path.unlink()
    if test_dir.exists():
        test_dir.rmdir()
    print(  # noqa: T201
    "UAT completed successfully.")

if __name__ == "__main__":
    run_uat()

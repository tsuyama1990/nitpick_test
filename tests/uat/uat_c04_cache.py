import os
import time
from pathlib import Path

import polars as pl

from src.processing.cache import LocalCache


def main() -> None:
    # Use a specific cache directory for UAT
    uat_cache_dir = Path(".cache/uat")
    if uat_cache_dir.exists():
        for file in uat_cache_dir.glob("*.parquet"):
            file.unlink()

    print("--- Running UAT-C04-01: Cache Hit Accuracy ---")  # noqa: T201
    cache = LocalCache(cache_dir=uat_cache_dir, ttl_seconds=3600)

    # GIVEN a pre-calculated Polars DataFrame representing aggregated commit data
    df = pl.DataFrame({"date": ["2024-01-01", "2024-01-02", "2024-01-03"], "commits": [10, 20, 15]})

    # WHEN the DataFrame is saved to the cache and immediately retrieved
    cache.set("uat_test_data", df)
    retrieved_df = cache.get("uat_test_data")

    # THEN the retrieved DataFrame must be structurally identical to the original DataFrame
    # AND all column data types must be perfectly preserved after the Parquet serialization round-trip
    assert retrieved_df is not None, "Failed to retrieve from cache"
    assert retrieved_df.equals(df), "Dataframes do not match!"
    print("UAT-C04-01 Passed!")  # noqa: T201

    print("\n--- Running UAT-C04-02: TTL Expiration Logic ---")  # noqa: T201
    # GIVEN a cached Parquet file containing historical commit data
    # AND the file's metadata indicates it was created 2 hours ago
    file_path = uat_cache_dir / "uat_test_data.parquet"
    past_time = time.time() - 7200  # 2 hours
    os.utime(file_path, (past_time, past_time))

    # WHEN the system attempts to retrieve the data from a cache configured with a 1-hour TTL
    # THEN the cache must report a cache miss (return None)
    expired_df = cache.get("uat_test_data")
    assert expired_df is None, "Cache returned stale data!"
    print("UAT-C04-02 Passed!")  # noqa: T201

    # Cleanup
    if file_path.exists():
        file_path.unlink()


if __name__ == "__main__":
    main()

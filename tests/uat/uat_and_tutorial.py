import os
import time
from pathlib import Path

import polars as pl

from src.processing.cache import LocalCache


def main() -> None:
    print("Running UAT-C04-01: Cache Hit Accuracy")  # noqa: T201
    # GIVEN a pre-calculated Polars DataFrame
    cache_dir = Path(".test_cache")
    cache = LocalCache(cache_dir=cache_dir)

    df = pl.DataFrame({"date": ["2024-01-01", "2024-01-02", "2024-01-03"], "commits": [10, 20, 15]})

    # WHEN the DataFrame is saved to the cache and immediately retrieved
    cache.set("commits_by_date", df)
    retrieved_df = cache.get("commits_by_date")

    # THEN the retrieved DataFrame must be structurally identical to the original DataFrame
    # AND all column data types must be perfectly preserved
    assert retrieved_df is not None, "Cache miss when hit was expected"
    assert retrieved_df.equals(df), "DataFrame content changed during cache round-trip"
    print("UAT-C04-01 Passed!")  # noqa: T201

    print("Running UAT-C04-02: TTL Expiration Logic")  # noqa: T201
    # GIVEN a cached Parquet file containing historical commit data
    # AND the file's metadata indicates it was created 2 hours ago
    ttl_seconds = 3600  # 1 hour
    cache_ttl = LocalCache(cache_dir=cache_dir, ttl_seconds=ttl_seconds)

    file_path = cache_dir / "commits_by_date.parquet"

    # simulate 2 hours ago
    current_time = time.time()
    two_hours_ago = current_time - 7200
    os.utime(file_path, (two_hours_ago, two_hours_ago))

    # WHEN the system attempts to retrieve the data from a cache configured with a 1-hour TTL
    stale_df = cache_ttl.get("commits_by_date")

    # THEN the cache must report a cache miss (return None)
    assert stale_df is None, "Cache returned data but file should be expired"
    print("UAT-C04-02 Passed!")  # noqa: T201

    # Cleanup
    if file_path.exists():
        file_path.unlink()
    if cache_dir.exists():
        cache_dir.rmdir()

    print("All UATs passed!")  # noqa: T201


if __name__ == "__main__":
    main()

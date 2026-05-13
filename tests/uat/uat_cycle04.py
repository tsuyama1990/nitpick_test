import contextlib
import os
import sys
import time
from pathlib import Path

# Setup paths to ensure src is importable
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

import polars as pl  # noqa: E402
from polars.testing import assert_frame_equal  # noqa: E402

from src.config import get_settings  # noqa: E402
from src.processing.cache import LocalCache  # noqa: E402


def uat_c04_01() -> None:
    print("--- Running UAT-C04-01: Cache Hit Accuracy ---")  # noqa: T201
    cache_dir = get_settings().uat_cache_dir
    cache = LocalCache(cache_dir=cache_dir)

    # GIVEN a pre-calculated Polars DataFrame representing aggregated commit data
    df = pl.DataFrame(
        {
            "date": ["2023-01-01", "2023-01-02", "2023-01-03"],
            "commits": [10, 20, 15],
            "active": [True, True, False],
        }
    )

    # WHEN the DataFrame is saved to the cache and immediately retrieved
    key = "uat_test_01"
    cache.set(key, df)
    retrieved_df = cache.get(key)

    # THEN the retrieved DataFrame must be structurally identical to the original DataFrame
    # AND all column data types must be perfectly preserved after the Parquet serialization round-trip.
    assert retrieved_df is not None, "Cache missed unexpectedly."
    assert_frame_equal(df, retrieved_df)
    print("✓ UAT-C04-01 Passed: DataFrame structural identity and data types are fully preserved.")  # noqa: T201

    # Cleanup
    (cache_dir / f"{key}.parquet").unlink()


def uat_c04_02() -> None:
    print("\n--- Running UAT-C04-02: TTL Expiration Logic ---")  # noqa: T201
    cache_dir = get_settings().uat_cache_dir
    # Configuring cache with 1-hour TTL (3600 seconds)
    cache = LocalCache(cache_dir=cache_dir, ttl_seconds=3600)

    # GIVEN a cached Parquet file containing historical commit data
    df = pl.DataFrame({"data": [1, 2, 3]})
    key = "uat_test_02"
    cache.set(key, df)

    # AND the file's metadata indicates it was created 2 hours ago (7200 seconds)
    file_path = cache_dir / f"{key}.parquet"
    past_time = time.time() - 7200
    os.utime(file_path, (past_time, past_time))

    # WHEN the system attempts to retrieve the data from a cache configured with a 1-hour TTL
    retrieved_df = cache.get(key)

    # THEN the cache must report a cache miss (return None)
    assert retrieved_df is None, "Cache incorrectly returned data instead of signaling a miss."
    print("✓ UAT-C04-02 Passed: Stale cache properly invalidated due to TTL logic.")  # noqa: T201

    # Cleanup
    file_path.unlink()
    with contextlib.suppress(OSError):
        cache_dir.rmdir()


if __name__ == "__main__":
    uat_c04_01()
    uat_c04_02()

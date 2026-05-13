import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import time

import polars as pl

from processing.cache import LocalCache


def run_uat() -> None:
    print("Running UAT-C04-01: Cache Hit Accuracy")  # noqa: T201
    cache_dir = Path(".uat_cache")
    cache = LocalCache(cache_dir=cache_dir)
    df = pl.DataFrame({"commits": [10, 20], "date": ["2024-01-01", "2024-01-02"]})
    cache.set("uat_hit_test", df)
    retrieved = cache.get("uat_hit_test")
    assert retrieved is not None
    assert retrieved.equals(df)
    print("✓ Cache Hit Accuracy Verified")  # noqa: T201

    print("\nRunning UAT-C04-02: TTL Expiration Logic")  # noqa: T201
    cache_ttl = LocalCache(cache_dir=cache_dir, ttl_seconds=2)
    cache_ttl.set("uat_ttl_test", df)

    # Verify it exists initially
    assert cache_ttl.get("uat_ttl_test") is not None
    print("Data saved successfully.")  # noqa: T201

    # Wait for expiration
    print("Waiting for TTL to expire (3 seconds)...")  # noqa: T201
    time.sleep(3)

    # Verify expiration
    miss = cache_ttl.get("uat_ttl_test")
    assert miss is None
    print("✓ TTL Expiration Logic Verified (Cache Miss)")  # noqa: T201

    # Cleanup
    import shutil

    shutil.rmtree(cache_dir)
    print("\nUAT completed successfully.")  # noqa: T201


if __name__ == "__main__":
    run_uat()

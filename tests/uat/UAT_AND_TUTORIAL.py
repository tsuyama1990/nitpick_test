import marimo

__generated_with = "0.10.15"
app = marimo.App(width="medium")


@app.cell
def _():
    import sys
    from pathlib import Path

    # Ensure src package is importable
    project_root = str(Path(__file__).parent.parent.parent)
    if project_root not in sys.path:
        sys.path.append(project_root)

    import os
    import time

    import polars as pl

    from src.config import get_settings
    from src.processing.cache import LocalCache

    return LocalCache, Path, get_settings, os, pl, sys, time


if __name__ == "__main__":
    app.run()


@app.cell
def _(LocalCache, Path, get_settings, pl):
    print("Running UAT-C04-01: Cache Hit Accuracy")
    settings = get_settings()
    cache_dir = Path(settings.uat_cache_root) / "hit"
    cache = LocalCache(cache_dir=cache_dir)

    # GIVEN a pre-calculated Polars DataFrame
    df = pl.DataFrame(
        {
            "date": pl.date_range(pl.date(2024, 1, 1), pl.date(2024, 1, 3), "1d", eager=True),
            "count": [10, 20, 30],
        }
    )
    print(f"Original DataFrame:\n{df}")

    # WHEN the DataFrame is saved to the cache and immediately retrieved
    cache.set("uat_hit_test", df)
    retrieved_df = cache.get("uat_hit_test")
    print(f"Retrieved DataFrame:\n{retrieved_df}")

    # THEN the retrieved DataFrame must be structurally identical to the original DataFrame
    # AND all column data types must be perfectly preserved
    assert retrieved_df is not None, "Retrieved DataFrame should not be None"
    assert retrieved_df.equals(df), "Retrieved DataFrame does not match the original DataFrame"
    print(
        "UAT-C04-01 Passed: Data structures and types perfectly preserved after serialization round-trip."
    )
    return cache_dir, df, retrieved_df


@app.cell
def _(LocalCache, Path, get_settings, os, pl, time):
    print("Running UAT-C04-02: TTL Expiration Logic")
    settings = get_settings()
    cache_dir = Path(settings.uat_cache_root) / "miss"
    ttl = settings.cache_ttl
    cache = LocalCache(cache_dir=cache_dir, ttl_seconds=ttl)

    from datetime import date

    # GIVEN a cached Parquet file containing historical commit data
    df = pl.DataFrame(
        {"date": [date(2024, 1, 1)], "count": [10]}, schema={"date": pl.Date, "count": pl.Int64}
    )
    cache.set("uat_miss_test", df)

    file_path = cache_dir / "uat_miss_test.parquet"
    assert file_path.exists(), "Cache file was not created"

    # AND the file's metadata indicates it was created 2 hours ago
    expired_time = time.time() - (ttl + 7200)  # 2 hours older than TTL
    os.utime(file_path, (expired_time, expired_time))

    print(f"File modification time artificially set to {expired_time}")

    # WHEN the system attempts to retrieve the data from a cache configured with a 1-hour TTL
    retrieved_df = cache.get("uat_miss_test")

    # THEN the cache must report a cache miss (return None)
    # AND signal to the upstream orchestrator that fresh data must be ingested
    assert retrieved_df is None, "Cache should return None for expired data"
    print("UAT-C04-02 Passed: Cache correctly invalidated stale data returning None.")
    return cache, cache_dir, df, expired_time, file_path, retrieved_df, ttl

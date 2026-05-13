import pathlib

import polars as pl

from src.processing.cache import LocalCache


def test_uat_c04_01_cache_hit_accuracy(tmp_path: pathlib.Path) -> None:
    """
    Scenario ID: UAT-C04-01
    Verify the local caching system successfully serializes and deserializes Polars DataFrames
    without data loss or schema alteration.
    """
    # GIVEN a pre-calculated Polars DataFrame representing aggregated commit data
    df = pl.DataFrame(
        {
            "author": ["alice", "bob", "alice"],
            "commits": [5, 2, 3],
        },
        schema={"author": pl.Utf8, "commits": pl.Int64},
    )

    cache = LocalCache(cache_dir=tmp_path)

    # WHEN the DataFrame is saved to the cache and immediately retrieved
    cache.set("uat_hit_accuracy", df)
    retrieved_df = cache.get("uat_hit_accuracy")

    # THEN the retrieved DataFrame must be structurally identical to the original DataFrame
    # AND all column data types must be perfectly preserved after the Parquet serialization round-trip
    assert retrieved_df is not None
    assert retrieved_df.schema == df.schema
    assert retrieved_df.equals(df)


def test_uat_c04_02_ttl_expiration_logic(tmp_path: pathlib.Path) -> None:
    """
    Scenario ID: UAT-C04-02
    Verify the caching system correctly invalidates stale data based on the TTL configuration.
    """
    # GIVEN a cached Parquet file containing historical commit data
    df = pl.DataFrame({"data": [1, 2, 3]})
    cache = LocalCache(cache_dir=tmp_path, ttl_seconds=3600)
    cache.set("uat_ttl_expiration", df)

    file_path = tmp_path / "uat_ttl_expiration.parquet"
    assert file_path.exists()

    # AND the file's metadata indicates it was created 2 hours ago
    now = pathlib.Path.stat(file_path).st_mtime
    two_hours_ago = now - 7200
    import os
    os.utime(file_path, (now, two_hours_ago))

    # WHEN the system attempts to retrieve the data from a cache configured with a 1-hour TTL
    retrieved_df = cache.get("uat_ttl_expiration")

    # THEN the cache must report a cache miss (return None)
    # AND signal to the upstream orchestrator that fresh data must be ingested from the external API
    assert retrieved_df is None

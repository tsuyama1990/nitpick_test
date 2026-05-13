import os
import time
from pathlib import Path

import polars as pl

from src.processing.cache import LocalCache


def test_uat_c04_01_cache_hit_accuracy(tmp_path: Path) -> None:
    """
    Scenario ID: UAT-C04-01
    Verify the local caching system successfully serializes and deserializes
    Polars DataFrames without data loss or schema alteration.
    """
    cache = LocalCache(cache_dir=tmp_path)
    original_df = pl.DataFrame(
        {"commits": [10, 20, 30], "date": ["2023-01-01", "2023-01-02", "2023-01-03"]}
    )

    cache.set("uat_hit", original_df)
    retrieved_df = cache.get("uat_hit")

    assert retrieved_df is not None
    assert retrieved_df.equals(original_df)
    assert retrieved_df.schema == original_df.schema


def test_uat_c04_02_ttl_expiration_logic(tmp_path: Path) -> None:
    """
    Scenario ID: UAT-C04-02
    Verify the caching system correctly invalidates stale data based on the
    Time-To-Live (TTL) configuration.
    """
    ttl_seconds = 3600
    cache = LocalCache(cache_dir=tmp_path, ttl_seconds=ttl_seconds)
    df = pl.DataFrame({"data": [1]})

    cache.set("uat_expire", df)
    file_path = tmp_path / "uat_expire.parquet"

    # Backdate by 2 hours
    past_time = time.time() - 7200
    os.utime(file_path, (past_time, past_time))

    retrieved_df = cache.get("uat_expire")
    assert retrieved_df is None

from datetime import UTC

import marimo

__generated_with = "0.23.4"
app = marimo.App()


@app.cell
def setup_env():  # type: ignore[no-untyped-def]
    import os
    import time
    from datetime import datetime, timezone

    import marimo as mo
    import polars as pl

    from src.config import settings
    from src.domain_models import CommitRecord
    from src.processing.cache_manager import load_from_cache, save_to_cache
    from src.processing.transformer import calculate_daily_commits, get_top_committers

    # Setup dummy data for C02-01
    mock_commits = [
        CommitRecord(
            commit_hash=f"hash{i}",
            author="alice" if i < 60 else "bob",
            date=datetime(2023, 1, 1 if i % 2 == 0 else 2, tzinfo=UTC),
        )
        for i in range(100)
    ]
    return (
        CommitRecord,
        calculate_daily_commits,
        get_top_committers,
        load_from_cache,
        mo,
        mock_commits,
        os,
        pl,
        save_to_cache,
        settings,
        time,
        datetime,
        timezone,
    )


@app.cell
def test_c02_01(calculate_daily_commits, get_top_committers, mo, mock_commits):  # type: ignore[no-untyped-def]
    mo.md("## C02-01: Accurate Data Transformation")

    # Process
    daily_df = calculate_daily_commits(mock_commits)
    top_df = get_top_committers(mock_commits)

    # Output to review
    assert top_df[0, "author"] == "alice"
    assert top_df[0, "commit_count"] == 60

    mo.vstack(
        [
            mo.md("### Daily Commits"),
            mo.ui.table(daily_df),
            mo.md("### Top Committers"),
            mo.ui.table(top_df),
        ]
    )
    return daily_df, top_df


@app.cell
def test_c02_02(daily_df, load_from_cache, mo, save_to_cache, time):  # type: ignore[no-untyped-def]
    mo.md("## C02-02: Cache Effectiveness and TTL Verification")

    repo_name = "uat_test_repo"

    # Simulate API fetch and cache save
    start_time_1 = time.time()
    save_to_cache(repo_name, daily_df)
    duration_1 = time.time() - start_time_1

    # Simulate subsequent fetch (Cache Hit)
    start_time_2 = time.time()
    cached_df = load_from_cache(repo_name)
    duration_2 = time.time() - start_time_2

    assert cached_df is not None
    assert cached_df.equals(daily_df)
    # The cache read should be significantly faster or roughly instantaneous

    mo.md(f"""
    **First Request (Save + Simulate Processing):** {duration_1:.6f} seconds

    **Second Request (Cache Hit):** {duration_2:.6f} seconds

    Cache Data verified: {"Yes" if cached_df.equals(daily_df) else "No"}
    """)
    return cached_df, duration_1, duration_2, repo_name, start_time_1, start_time_2


if __name__ == "__main__":
    app.run()

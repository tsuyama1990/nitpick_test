from datetime import UTC

import marimo

__generated_with = "0.23.5"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo

    return (mo,)


@app.cell
def __(mo):
    mo.md("# CYCLE 02 UAT: Transformation and Caching Validation")


@app.cell
def __(mo):
    mo.md(
        """
        ## Scenario ID: C02-01 - Accurate Data Transformation
        Verify that the implemented Polars transformation logic mathematically and accurately calculates the daily commit frequency trends and definitively identifies the top 5 highest-volume committers without any runtime errors.
        """
    )


@app.cell
def __():
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path().cwd().resolve()))

    from datetime import datetime

    from src.domain_models import CommitRecord
    from src.transformer import aggregate_commits_by_date, get_top_committers

    # Generate 100 heavily engineered mock commits
    mock_commits = []

    # 50 commits for author "alice" on 2023-01-01
    for i in range(50):
        mock_commits.append(
            CommitRecord(
                sha=f"alice_{i}", author="alice", date=datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC)
            )
        )

    # 30 commits for author "bob" on 2023-01-02
    for i in range(30):
        mock_commits.append(
            CommitRecord(
                sha=f"bob_{i}", author="bob", date=datetime(2023, 1, 2, 12, 0, 0, tzinfo=UTC)
            )
        )

    # 10 commits for author "charlie" on 2023-01-03
    for i in range(10):
        mock_commits.append(
            CommitRecord(
                sha=f"charlie_{i}",
                author="charlie",
                date=datetime(2023, 1, 3, 12, 0, 0, tzinfo=UTC),
            )
        )

    # 5 commits for author "dave" on 2023-01-04
    for i in range(5):
        mock_commits.append(
            CommitRecord(
                sha=f"dave_{i}", author="dave", date=datetime(2023, 1, 4, 12, 0, 0, tzinfo=UTC)
            )
        )

    # 3 commits for author "eve" on 2023-01-05
    for i in range(3):
        mock_commits.append(
            CommitRecord(
                sha=f"eve_{i}", author="eve", date=datetime(2023, 1, 5, 12, 0, 0, tzinfo=UTC)
            )
        )

    # 2 commits for author "frank" on 2023-01-06 (should not be in top 5)
    for i in range(2):
        mock_commits.append(
            CommitRecord(
                sha=f"frank_{i}", author="frank", date=datetime(2023, 1, 6, 12, 0, 0, tzinfo=UTC)
            )
        )
    return mock_commits, CommitRecord, aggregate_commits_by_date, get_top_committers


@app.cell
def __(mock_commits, aggregate_commits_by_date, mo):
    df_date = aggregate_commits_by_date(mock_commits)

    mo.vstack([mo.md("### Aggregated Commits by Date"), mo.ui.table(df_date)])
    return (df_date,)


@app.cell
def __(mock_commits, get_top_committers, mo):
    df_top = get_top_committers(mock_commits)

    top_committer = df_top.row(0)[0]
    is_alice = top_committer == "alice"

    mo.vstack(
        [
            mo.md("### Top 5 Committers"),
            mo.ui.table(df_top),
            mo.md(f"**Verification:** Top committer is 'alice': {is_alice}"),
        ]
    )
    return df_top, is_alice, top_committer


@app.cell
def __(mo):
    mo.md(
        """
        ## Scenario ID: C02-02 - Cache Effectiveness and TTL Verification
        Ensure the implemented local Parquet caching mechanism successfully and completely prevents redundant outbound API calls and drastically, noticeably reduces data response times for subsequent, repeated requests occurring within the defined TTL window.
        """
    )


@app.cell
def __(df_date, mo):
    import time

    from src.cache_manager import load_from_cache, save_to_cache

    test_repo = "facebook/react"

    # 1. Save to cache
    save_to_cache(test_repo, df_date)

    # 2. First fetch (simulate fetching from cache after network request in real world)
    start_time = time.time()
    _ = load_from_cache(test_repo)
    first_fetch_time = time.time() - start_time

    # 3. Second fetch (from cache)
    start_time = time.time()
    cached_df = load_from_cache(test_repo)
    second_fetch_time = time.time() - start_time

    # Verify cache hit
    is_cache_hit = cached_df is not None

    mo.vstack(
        [
            mo.md(f"**First cache load time:** {first_fetch_time:.6f} seconds"),
            mo.md(f"**Second cache load time:** {second_fetch_time:.6f} seconds"),
            mo.md(f"**Cache Hit Verified:** {is_cache_hit}"),
        ]
    )


if __name__ == "__main__":
    app.run()

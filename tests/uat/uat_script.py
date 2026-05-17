import polars as pl

from src.processing.transformations import aggregate_commits_by_date, get_top_committers


def run_uat() -> None:
    print("Running UAT-C03-01: Date Aggregation Accuracy")  # noqa: T201
    raw_commits_01 = [
        {"name": "UserA", "date": "2023-01-01T10:00:00Z"},
        {"name": "UserB", "date": "2023-01-01T11:00:00Z"},
        {"name": "UserA", "date": "2023-01-02T10:00:00Z"},
    ]
    df_date = aggregate_commits_by_date(raw_commits_01)  # type: ignore[arg-type]

    assert df_date.schema["date"] == pl.Date, f"Expected Date type, got {df_date.schema['date']}"
    assert df_date.schema["commit_count"] == pl.UInt32, (
        f"Expected UInt32 type, got {df_date.schema['commit_count']}"
    )
    assert df_date["commit_count"].sum() == len(raw_commits_01), (
        "Total sum of commit_count does not equal input records"
    )
    print("✓ UAT-C03-01 passed.")  # noqa: T201

    print("Running UAT-C03-02: Deterministic Top Committers")  # noqa: T201
    raw_commits_02 = [
        {"name": "Charlie", "date": "2023-01-01T10:00:00Z"},
        {"name": "Charlie", "date": "2023-01-01T11:00:00Z"},
        {"name": "Alice", "date": "2023-01-02T10:00:00Z"},
        {"name": "Alice", "date": "2023-01-02T11:00:00Z"},
        {"name": "Bob", "date": "2023-01-03T10:00:00Z"},
        {"name": "Bob", "date": "2023-01-03T11:00:00Z"},
    ]

    # Alice, Bob, Charlie all have 2 commits.
    # Top 2 committers should be Alice and Bob due to alphabetical sort.
    df_committers = get_top_committers(raw_commits_02, top_n=2)  # type: ignore[arg-type]

    results = df_committers.to_dicts()
    assert len(results) == 2, "Expected 2 top committers"
    assert results[0]["name"] == "Alice", (
        f"Expected Alice to be top committer, got {results[0]['name']}"
    )
    assert results[1]["name"] == "Bob", (
        f"Expected Bob to be second top committer, got {results[1]['name']}"
    )
    print("✓ UAT-C03-02 passed.")  # noqa: T201


if __name__ == "__main__":
    run_uat()

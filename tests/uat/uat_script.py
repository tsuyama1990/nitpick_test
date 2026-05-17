import polars as pl

from src.processing.transformations import aggregate_commits_by_date, get_top_committers


def test_uat_c03_01_date_aggregation() -> None:
    # UAT-C03-01: Date Aggregation Accuracy
    raw_commits = [
        {"commit": {"author": {"name": "Alice", "date": "2023-01-01T10:00:00Z"}}},
        {"commit": {"author": {"name": "Alice", "date": "2023-01-01T12:00:00Z"}}},
        {"commit": {"author": {"name": "Bob", "date": "2023-01-02T14:00:00Z"}}},
    ]
    df = aggregate_commits_by_date(raw_commits)  # type: ignore[arg-type]

    assert "date" in df.columns
    assert "commit_count" in df.columns
    assert df.select(pl.col("commit_count").sum()).item() == 3
    print("UAT-C03-01 Passed")  # noqa: T201


def test_uat_c03_02_deterministic_top_committers() -> None:
    # UAT-C03-02: Deterministic Top Committers
    raw_commits = [
        {"commit": {"author": {"name": "Charlie", "date": "2023-01-01T10:00:00Z"}}},
        {"commit": {"author": {"name": "Bob", "date": "2023-01-01T11:00:00Z"}}},
        {"commit": {"author": {"name": "Alice", "date": "2023-01-01T12:00:00Z"}}},
    ]
    # All have 1 commit. Sort should be Alice, Bob, Charlie alphabetically.
    df = get_top_committers(raw_commits, top_n=2)  # type: ignore[arg-type]

    names = df["name"].to_list()
    assert names == ["Alice", "Bob"]
    print("UAT-C03-02 Passed")  # noqa: T201


if __name__ == "__main__":
    test_uat_c03_01_date_aggregation()
    test_uat_c03_02_deterministic_top_committers()

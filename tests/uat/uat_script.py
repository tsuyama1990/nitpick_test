import polars as pl

from src.processing.transformations import aggregate_commits_by_date, get_top_committers


def run_uat_c03_01() -> None:
    print("Running UAT-C03-01: Date Aggregation Accuracy")  # noqa: T201
    raw_commits: list[dict[str, object]] = [
        {"commit": {"author": {"name": "Alice", "date": "2023-10-27T10:00:00Z"}}},
        {"commit": {"author": {"name": "Bob", "date": "2023-10-27T11:00:00Z"}}},
        {"commit": {"author": {"name": "Alice", "date": "2023-10-28T10:00:00Z"}}},
    ]
    df = aggregate_commits_by_date(raw_commits)

    assert df.schema["date"] == pl.Date, "Schema for 'date' must be pl.Date"
    assert "commit_count" in df.columns, "Missing 'commit_count' column"
    assert df["commit_count"].sum() == len(raw_commits), "Total commit count mismatch"

    print("UAT-C03-01 Passed.")  # noqa: T201


def run_uat_c03_02() -> None:
    print("Running UAT-C03-02: Deterministic Top Committers")  # noqa: T201
    raw_commits: list[dict[str, object]] = [
        {"commit": {"author": {"name": "Charlie", "date": "2023-10-27T10:00:00Z"}}},
        {"commit": {"author": {"name": "Charlie", "date": "2023-10-27T11:00:00Z"}}},
        {"commit": {"author": {"name": "Alice", "date": "2023-10-28T10:00:00Z"}}},
        {"commit": {"author": {"name": "Alice", "date": "2023-10-28T11:00:00Z"}}},
        {"commit": {"author": {"name": "Bob", "date": "2023-10-29T10:00:00Z"}}},
        {"commit": {"author": {"name": "Bob", "date": "2023-10-29T11:00:00Z"}}},
    ]
    df = get_top_committers(raw_commits, top_n=2)
    names = df["name"].to_list()
    assert names == ["Alice", "Bob"], f"Expected ['Alice', 'Bob'], got {names}"

    print("UAT-C03-02 Passed.")  # noqa: T201


if __name__ == "__main__":
    run_uat_c03_01()
    run_uat_c03_02()

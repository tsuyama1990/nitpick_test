import polars as pl

from src.processing.transformations import aggregate_commits_by_date, get_top_committers


def verify_uat_c03_01() -> None:
    print("--- UAT-C03-01: Date Aggregation Accuracy ---")  # noqa: T201
    mock_data: list[dict[str, object]] = [
        {"commit": {"author": {"name": "Alice", "date": "2023-10-01T10:00:00Z"}}},
        {"commit": {"author": {"name": "Bob", "date": "2023-10-01T12:00:00Z"}}},
        {"commit": {"author": {"name": "Charlie", "date": "2023-10-02T10:00:00Z"}}},
    ]
    df = aggregate_commits_by_date(mock_data)
    assert "date" in df.columns
    assert "commit_count" in df.columns
    assert df.schema["date"] == pl.Date

    total_commits = df["commit_count"].sum()
    assert total_commits == len(mock_data), (
        f"Expected {len(mock_data)} total commits, got {total_commits}"
    )
    print("PASS: Date aggregation accurately matches input count and schema.")  # noqa: T201


def verify_uat_c03_02() -> None:
    print("--- UAT-C03-02: Deterministic Top Committers ---")  # noqa: T201
    mock_data: list[dict[str, object]] = [
        {"commit": {"author": {"name": "Charlie", "date": "2023-10-01T10:00:00Z"}}},
        {"commit": {"author": {"name": "Bob", "date": "2023-10-01T12:00:00Z"}}},
        {"commit": {"author": {"name": "Alice", "date": "2023-10-02T10:00:00Z"}}},
        {"commit": {"author": {"name": "Charlie", "date": "2023-10-02T11:00:00Z"}}},
        {"commit": {"author": {"name": "Bob", "date": "2023-10-03T10:00:00Z"}}},
        {"commit": {"author": {"name": "Alice", "date": "2023-10-03T11:00:00Z"}}},
    ]

    # Alice, Bob, Charlie all have 2 commits.
    df = get_top_committers(mock_data, top_n=2)
    names = df["name"].to_list()

    assert names == ["Alice", "Bob"], f"Expected ['Alice', 'Bob'], got {names}"
    print("PASS: Deterministic tie-breaking correctly applied alphabetical order.")  # noqa: T201


if __name__ == "__main__":
    verify_uat_c03_01()
    verify_uat_c03_02()

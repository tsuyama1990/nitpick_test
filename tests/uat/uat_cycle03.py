from datetime import date
from typing import Any

from src.processing.transformations import aggregate_commits_by_date, get_top_committers


def verify_uat_c03_01() -> None:
    print("--- UAT-C03-01: Date Aggregation Accuracy ---")  # noqa: T201
    mock_dataset: list[dict[str, Any]] = [
        {"commit": {"author": {"name": "UserA", "date": "2023-10-01T10:00:00Z"}}},
        {"commit": {"author": {"name": "UserB", "date": "2023-10-01T11:00:00Z"}}},
        {"commit": {"author": {"name": "UserC", "date": "2023-10-02T10:00:00Z"}}},
    ]
    df = aggregate_commits_by_date(mock_dataset)

    assert str(df.schema["date"]) == "Date", f"Expected Date type, got {df.schema['date']}"
    assert "commit_count" in df.schema

    total_commits = df["commit_count"].sum()
    assert total_commits == len(mock_dataset), (
        f"Expected sum {len(mock_dataset)}, got {total_commits}"
    )

    res = df.to_dicts()
    assert res == [
        {"date": date(2023, 10, 1), "commit_count": 2},
        {"date": date(2023, 10, 2), "commit_count": 1},
    ]
    print("✓ UAT-C03-01 Passed: Aggregation accuracy verified.")  # noqa: T201


def verify_uat_c03_02() -> None:
    print("--- UAT-C03-02: Deterministic Top Committers ---")  # noqa: T201
    mock_dataset: list[dict[str, Any]] = [
        {"commit": {"author": {"name": "Charlie", "date": "2023-10-01T10:00:00Z"}}},
        {"commit": {"author": {"name": "Charlie", "date": "2023-10-01T11:00:00Z"}}},
        {"commit": {"author": {"name": "Alice", "date": "2023-10-02T10:00:00Z"}}},
        {"commit": {"author": {"name": "Alice", "date": "2023-10-02T11:00:00Z"}}},
        {"commit": {"author": {"name": "Bob", "date": "2023-10-03T10:00:00Z"}}},
        {"commit": {"author": {"name": "Bob", "date": "2023-10-03T11:00:00Z"}}},
    ]

    df = get_top_committers(mock_dataset, top_n=2)
    res = df.to_dicts()

    # Alice and Bob should be top 2 out of the 3 tied users due to alphabetical sort
    assert len(res) == 2
    assert res[0]["name"] == "Alice"
    assert res[1]["name"] == "Bob"

    print("✓ UAT-C03-02 Passed: Deterministic top committers tie-breaking verified.")  # noqa: T201


if __name__ == "__main__":
    verify_uat_c03_01()
    print("\n")  # noqa: T201
    verify_uat_c03_02()

from typing import Any

from src.processing.transformations import aggregate_commits_by_date, get_top_committers


def verify_date_aggregation() -> None:
    print("Running UAT-C03-01: Date Aggregation Accuracy")  # noqa: T201

    mock_dataset: list[dict[str, Any]] = [
        {"date": "2023-01-01T10:00:00Z", "name": "Alice"},
        {"date": "2023-01-01T12:00:00Z", "name": "Bob"},
        {"date": "2023-01-02T10:00:00Z", "name": "Alice"},
    ]

    df = aggregate_commits_by_date(mock_dataset)
    print(f"Resulting DataFrame:\n{df}")  # noqa: T201

    total_commits = df["commit_count"].sum()
    assert total_commits == 3, f"Expected 3 commits, got {total_commits}"

    print("UAT-C03-01 Passed.\n")  # noqa: T201


def verify_deterministic_sorting() -> None:
    print("Running UAT-C03-02: Deterministic Top Committers")  # noqa: T201

    mock_dataset: list[dict[str, Any]] = [
        {"date": "2023-01-01T10:00:00Z", "name": "Charlie"},
        {"date": "2023-01-01T11:00:00Z", "name": "Bob"},
        {"date": "2023-01-01T12:00:00Z", "name": "Alice"},
    ]

    df = get_top_committers(mock_dataset, top_n=2)
    print(f"Resulting DataFrame:\n{df}")  # noqa: T201

    names = df["name"].to_list()
    assert names == ["Alice", "Bob"], f"Expected ['Alice', 'Bob'], got {names}"

    print("UAT-C03-02 Passed.\n")  # noqa: T201


if __name__ == "__main__":
    verify_date_aggregation()
    verify_deterministic_sorting()

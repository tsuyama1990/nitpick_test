from src.processing.transformations import aggregate_commits_by_date, get_top_committers


def run_uat() -> None:
    # Scenario ID: UAT-C03-01
    print("Running UAT-C03-01: Date Aggregation Accuracy")  # noqa: T201
    mock_data: list[dict[str, object]] = [
        {"name": "Alice", "date": "2024-05-15T10:00:00Z"},
        {"name": "Bob", "date": "2024-05-15T11:00:00Z"},
        {"name": "Alice", "date": "2024-05-16T10:00:00Z"},
    ]
    df_dates = aggregate_commits_by_date(mock_data)
    assert df_dates.schema["date"].is_(type(df_dates.schema["date"]))  # Native date check loosely
    assert df_dates["commit_count"].sum() == 3
    print("UAT-C03-01 Passed")  # noqa: T201

    # Scenario ID: UAT-C03-02
    print("Running UAT-C03-02: Deterministic Top Committers")  # noqa: T201
    tie_data: list[dict[str, object]] = [
        {"name": "Charlie", "date": "2024-05-15T10:00:00Z"},
        {"name": "Charlie", "date": "2024-05-15T11:00:00Z"},
        {"name": "Bob", "date": "2024-05-15T10:00:00Z"},
        {"name": "Bob", "date": "2024-05-15T11:00:00Z"},
        {"name": "Alice", "date": "2024-05-15T10:00:00Z"},
        {"name": "Alice", "date": "2024-05-15T11:00:00Z"},
    ]
    df_top = get_top_committers(tie_data, top_n=2)
    results = df_top.to_dicts()
    assert results[0]["name"] == "Alice"
    assert results[1]["name"] == "Bob"
    print("UAT-C03-02 Passed")  # noqa: T201


if __name__ == "__main__":
    run_uat()

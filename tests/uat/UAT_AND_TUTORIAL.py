import marimo

__generated_with = "0.4.0"
app = marimo.App()


@app.cell
def __():
    import sys
    from pathlib import Path

    sys.path.append(str(Path(__file__).parent.parent.parent))

    import polars as pl
    from src.processing.transformations import aggregate_commits_by_date, get_top_committers

    return aggregate_commits_by_date, get_top_committers, pl


@app.cell
def __(aggregate_commits_by_date):
    print("### Scenario UAT-C03-01: Date Aggregation Accuracy")
    mock_data = [
        {"commit": {"author": {"name": "User", "date": "2024-01-01T10:00:00Z"}}},
        {"commit": {"author": {"name": "User", "date": "2024-01-01T11:00:00Z"}}},
        {"commit": {"author": {"name": "User", "date": "2024-01-02T10:00:00Z"}}},
    ]
    df_date = aggregate_commits_by_date(mock_data)
    print("Date Aggregation DataFrame:")
    print(df_date)
    assert df_date["commit_count"].sum() == 3
    assert "date" in df_date.columns
    print("✓ UAT-C03-01 Passed")
    return df_date, mock_data


@app.cell
def __(get_top_committers):
    print("### Scenario UAT-C03-02: Deterministic Top Committers")
    mock_tie_data = [
        {"commit": {"author": {"name": "Charlie", "date": "2024-01-01T10:00:00Z"}}},
        {"commit": {"author": {"name": "Charlie", "date": "2024-01-01T11:00:00Z"}}},
        {"commit": {"author": {"name": "Bob", "date": "2024-01-02T10:00:00Z"}}},
        {"commit": {"author": {"name": "Bob", "date": "2024-01-02T11:00:00Z"}}},
        {"commit": {"author": {"name": "Alice", "date": "2024-01-03T10:00:00Z"}}},
        {"commit": {"author": {"name": "Alice", "date": "2024-01-03T11:00:00Z"}}},
    ]
    df_top = get_top_committers(mock_tie_data, top_n=2)
    print("Top Committers DataFrame:")
    print(df_top)
    authors = df_top["name"].to_list()
    assert authors == ["Alice", "Bob"]
    print("✓ UAT-C03-02 Passed")
    return df_top, mock_tie_data


if __name__ == "__main__":
    app.run()

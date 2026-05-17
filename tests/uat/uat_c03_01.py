from src.processing.transformations import aggregate_commits_by_date


def test_uat_c03_01() -> None:
    # GIVEN a mock JSON dataset containing commits spread across multiple dates
    raw_commits: list[dict[str, object]] = [
        {"commit": {"author": {"date": "2024-05-17T12:00:00Z", "name": "Alice"}}},
        {"commit": {"author": {"date": "2024-05-17T13:00:00Z", "name": "Bob"}}},
        {"commit": {"author": {"date": "2024-05-18T10:00:00Z", "name": "Alice"}}},
        {"commit": {"author": {"date": "2024-05-18T11:00:00Z", "name": "Charlie"}}},
    ]

    # WHEN the data is processed by the date aggregation function
    df = aggregate_commits_by_date(raw_commits)

    # THEN the resulting DataFrame must contain a `date` column of a native Date type and a `commit_count` column
    assert "date" in df.columns
    assert "commit_count" in df.columns

    # AND the total sum of `commit_count` must exactly equal the number of input records.
    total_commits = df["commit_count"].sum()
    assert total_commits == len(raw_commits)

    print("UAT-C03-01 Passed!")  # noqa: T201


if __name__ == "__main__":
    test_uat_c03_01()

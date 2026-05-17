from src.processing.transformations import get_top_committers


def test_uat_c03_02() -> None:
    # GIVEN a mock dataset where users "Alice", "Bob", and "Charlie" each have an identical number of commits
    raw_commits: list[dict[str, object]] = [
        {"commit": {"author": {"date": "2024-05-17T12:00:00Z", "name": "Charlie"}}},
        {"commit": {"author": {"date": "2024-05-18T12:00:00Z", "name": "Charlie"}}},
        {"commit": {"author": {"date": "2024-05-17T13:00:00Z", "name": "Bob"}}},
        {"commit": {"author": {"date": "2024-05-18T13:00:00Z", "name": "Bob"}}},
        {"commit": {"author": {"date": "2024-05-17T14:00:00Z", "name": "Alice"}}},
        {"commit": {"author": {"date": "2024-05-18T14:00:00Z", "name": "Alice"}}},
    ]

    # WHEN the data is processed to find the top 2 committers
    df = get_top_committers(raw_commits, top_n=2)

    # THEN the system must consistently return "Alice" and "Bob" based on alphabetical tie-breaking
    # AND the application must not exhibit flaky behavior or random result ordering across multiple executions.
    results = df.to_dicts()
    assert len(results) == 2

    assert results[0]["name"] == "Alice"
    assert results[1]["name"] == "Bob"

    print("UAT-C03-02 Passed!")  # noqa: T201


if __name__ == "__main__":
    test_uat_c03_02()

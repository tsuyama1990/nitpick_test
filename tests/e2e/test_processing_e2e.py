from datetime import date

from src.processing.transformations import aggregate_commits_by_date, get_top_committers


def test_processing_e2e_flow() -> None:
    data: list[dict[str, object]] = [
        {"name": "E2E User", "date": "2024-05-15T10:00:00Z"},
        {"name": "E2E User", "date": "2024-05-16T10:00:00Z"},
        {"name": "E2E User 2", "date": "2024-05-15T12:00:00Z"},
    ]

    # 1. Test Aggregation by Date
    date_df = aggregate_commits_by_date(data)
    assert len(date_df) == 2
    date_results = date_df.to_dicts()
    assert date_results[0] == {"date": date(2024, 5, 15), "commit_count": 2}
    assert date_results[1] == {"date": date(2024, 5, 16), "commit_count": 1}

    # 2. Test Top Committers
    committer_df = get_top_committers(data, top_n=1)
    assert len(committer_df) == 1
    committer_results = committer_df.to_dicts()
    assert committer_results[0] == {"name": "E2E User", "commit_count": 2}

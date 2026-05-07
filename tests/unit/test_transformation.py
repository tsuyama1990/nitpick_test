from datetime import UTC, datetime

import polars as pl

from src.domain_models import Commit
from src.transformation.processor import DataTransformer


def test_data_transformer_empty() -> None:
    transformer = DataTransformer()
    by_date, top_users = transformer.process_commits([])
    assert isinstance(by_date, pl.DataFrame)
    assert isinstance(top_users, pl.DataFrame)
    assert len(by_date) == 0
    assert len(top_users) == 0


def test_data_transformer_success() -> None:
    dt1 = datetime(2023, 1, 1, 10, 0, 0, tzinfo=UTC)
    dt2 = datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC)
    dt3 = datetime(2023, 1, 2, 10, 0, 0, tzinfo=UTC)

    commits = [
        Commit(sha="1", commit={"committer": {"name": "Alice", "date": dt1}}),  # type: ignore[arg-type]
        Commit(sha="2", commit={"committer": {"name": "Bob", "date": dt2}}),  # type: ignore[arg-type]
        Commit(sha="3", commit={"committer": {"name": "Alice", "date": dt3}}),  # type: ignore[arg-type]
    ]

    transformer = DataTransformer()
    by_date, top_users = transformer.process_commits(commits)

    assert len(by_date) == 2
    # Verify date aggregation
    date_dict = dict(
        zip(by_date["date"].to_list(), by_date["commit_count"].to_list(), strict=False)
    )
    assert date_dict["2023-01-01"] == 2
    assert date_dict["2023-01-02"] == 1

    assert len(top_users) == 2
    # Verify user aggregation
    user_dict = dict(
        zip(top_users["name"].to_list(), top_users["commit_count"].to_list(), strict=False)
    )
    assert user_dict["Alice"] == 2
    assert user_dict["Bob"] == 1

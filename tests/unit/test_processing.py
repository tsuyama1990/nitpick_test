from datetime import UTC, datetime

import polars as pl
import pytest
from pydantic import ValidationError

from src.processing.transformations import aggregate_commits_by_date, get_top_committers


def test_aggregate_commits_by_date_valid() -> None:
    raw_commits = [
        {"commit": {"author": {"name": "Alice", "date": "2023-01-01T10:00:00Z"}}},
        {"commit": {"author": {"name": "Alice", "date": "2023-01-01T12:00:00Z"}}},
        {"commit": {"author": {"name": "Bob", "date": "2023-01-01T14:00:00Z"}}},
        {"commit": {"author": {"name": "Charlie", "date": "2023-01-02T10:00:00Z"}}},
        {"commit": {"author": {"name": "Dave", "date": "2023-01-03T10:00:00Z"}}},
    ]
    df = aggregate_commits_by_date(raw_commits)  # type: ignore[arg-type]

    assert isinstance(df, pl.DataFrame)
    assert df.columns == ["date", "commit_count"]
    assert df.dtypes == [pl.Date, pl.UInt32]

    result = df.to_dicts()
    assert len(result) == 3
    assert result[0] == {"date": datetime(2023, 1, 1, tzinfo=UTC).date(), "commit_count": 3}
    assert result[1] == {"date": datetime(2023, 1, 2, tzinfo=UTC).date(), "commit_count": 1}
    assert result[2] == {"date": datetime(2023, 1, 3, tzinfo=UTC).date(), "commit_count": 1}


def test_aggregate_commits_by_date_empty() -> None:
    df = aggregate_commits_by_date([])
    assert isinstance(df, pl.DataFrame)
    assert df.columns == ["date", "commit_count"]
    assert df.dtypes == [pl.Date, pl.UInt32]
    assert len(df) == 0


def test_get_top_committers_valid_and_deterministic_sort() -> None:
    raw_commits = [
        {"commit": {"author": {"name": "Charlie", "date": "2023-01-01T10:00:00Z"}}},
        {"commit": {"author": {"name": "Charlie", "date": "2023-01-01T11:00:00Z"}}},
        {"commit": {"author": {"name": "Alice", "date": "2023-01-01T12:00:00Z"}}},
        {"commit": {"author": {"name": "Alice", "date": "2023-01-01T13:00:00Z"}}},
        {"commit": {"author": {"name": "Bob", "date": "2023-01-01T14:00:00Z"}}},
        {"commit": {"author": {"name": "Bob", "date": "2023-01-01T15:00:00Z"}}},
    ]
    # Alice, Bob, and Charlie each have 2 commits.
    # Sorting descending by count, then ascending by name alphabetically should return Alice, then Bob, then Charlie.
    df = get_top_committers(raw_commits, top_n=2)  # type: ignore[arg-type]

    assert isinstance(df, pl.DataFrame)
    assert df.columns == ["name", "commit_count"]
    # Types might be Utf8 and UInt32
    assert df.dtypes[0] in [pl.Utf8, pl.String]
    assert df.dtypes[1] == pl.UInt32

    result = df.to_dicts()
    assert len(result) == 2
    assert result[0] == {"name": "Alice", "commit_count": 2}
    assert result[1] == {"name": "Bob", "commit_count": 2}


def test_get_top_committers_empty() -> None:
    df = get_top_committers([])
    assert isinstance(df, pl.DataFrame)
    assert df.columns == ["name", "commit_count"]
    assert len(df) == 0


def test_pydantic_validation_error() -> None:
    malformed_commits = [
        {"commit": {"author": {"name": "Alice"}}}  # Missing date
    ]
    with pytest.raises(ValidationError):
        aggregate_commits_by_date(malformed_commits)  # type: ignore[arg-type]

    with pytest.raises(ValidationError):
        get_top_committers(malformed_commits)  # type: ignore[arg-type]


def test_validation_error_not_dict_commit() -> None:
    malformed_commits = [{"commit": "not a dict"}]
    with pytest.raises(ValidationError):
        aggregate_commits_by_date(malformed_commits)  # type: ignore[arg-type]
    with pytest.raises(ValidationError):
        get_top_committers(malformed_commits)  # type: ignore[arg-type]


def test_validation_error_not_dict_author() -> None:
    malformed_commits = [{"commit": {"author": "not a dict"}}]
    with pytest.raises(ValidationError):
        aggregate_commits_by_date(malformed_commits)  # type: ignore[arg-type]
    with pytest.raises(ValidationError):
        get_top_committers(malformed_commits)  # type: ignore[arg-type]


def test_other_exception() -> None:
    # test other exception than validation error during initialization
    class FakeDict(dict[str, object]):
        def __getitem__(self, key: str) -> object:
            err_msg = "Some other error"
            raise ValueError(err_msg)

    malformed_commits = [FakeDict()]
    with pytest.raises(ValidationError):
        aggregate_commits_by_date(malformed_commits)  # type: ignore[arg-type]
    with pytest.raises(ValidationError):
        get_top_committers(malformed_commits)  # type: ignore[arg-type]

def test_validation_error_not_dict_rc() -> None:
    malformed_commits = ["not a dict"]
    with pytest.raises(ValidationError):
        aggregate_commits_by_date(malformed_commits) # type: ignore[arg-type]
    with pytest.raises(ValidationError):
        get_top_committers(malformed_commits) # type: ignore[arg-type]

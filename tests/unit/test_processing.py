from collections.abc import Callable

import polars as pl
import pytest
from pydantic import ValidationError

from src.processing.transformations import aggregate_commits_by_date, get_top_committers


def test_aggregate_commits_by_date_valid() -> None:
    raw_data: list[dict[str, object]] = [
        {"commit": {"author": {"name": "Alice", "date": "2023-10-01T10:00:00Z"}}},
        {"commit": {"author": {"name": "Bob", "date": "2023-10-01T12:00:00Z"}}},
        {"commit": {"author": {"name": "Alice", "date": "2023-10-02T10:00:00Z"}}},
    ]

    df = aggregate_commits_by_date(raw_data)

    assert isinstance(df, pl.DataFrame)
    assert df.columns == ["date", "commit_count"]
    assert df.schema["date"] == pl.Date

    results = df.to_dicts()
    assert len(results) == 2
    assert results[0]["commit_count"] == 2  # Oct 1
    assert results[1]["commit_count"] == 1  # Oct 2


def test_get_top_committers_valid() -> None:
    raw_data: list[dict[str, object]] = [
        {"commit": {"author": {"name": "Alice", "date": "2023-10-01T10:00:00Z"}}},
        {"commit": {"author": {"name": "Bob", "date": "2023-10-01T12:00:00Z"}}},
        {"commit": {"author": {"name": "Alice", "date": "2023-10-02T10:00:00Z"}}},
        {"commit": {"author": {"name": "Charlie", "date": "2023-10-03T10:00:00Z"}}},
    ]

    df = get_top_committers(raw_data, top_n=2)

    assert isinstance(df, pl.DataFrame)
    assert df.columns == ["name", "commit_count"]
    assert df.schema["name"] == pl.String

    results = df.to_dicts()
    assert len(results) == 2
    assert results[0]["name"] == "Alice"
    assert results[0]["commit_count"] == 2
    assert results[1]["name"] == "Bob"
    assert results[1]["commit_count"] == 1


def test_get_top_committers_deterministic_sorting() -> None:
    # 3 authors, 2 commits each.
    raw_data: list[dict[str, object]] = [
        {"commit": {"author": {"name": "Charlie", "date": "2023-10-01T10:00:00Z"}}},
        {"commit": {"author": {"name": "Alice", "date": "2023-10-01T12:00:00Z"}}},
        {"commit": {"author": {"name": "Bob", "date": "2023-10-02T10:00:00Z"}}},
        {"commit": {"author": {"name": "Alice", "date": "2023-10-02T11:00:00Z"}}},
        {"commit": {"author": {"name": "Charlie", "date": "2023-10-03T10:00:00Z"}}},
        {"commit": {"author": {"name": "Bob", "date": "2023-10-03T11:00:00Z"}}},
    ]

    # We ask for top 2. Because of alphabetical secondary sort, Alice and Bob should win.
    df = get_top_committers(raw_data, top_n=2)
    results = df.to_dicts()

    assert len(results) == 2
    assert results[0]["name"] == "Alice"
    assert results[1]["name"] == "Bob"




@pytest.mark.parametrize(
    ("func", "expected_columns", "schema_col", "schema_type"),
    [
        (aggregate_commits_by_date, ["date", "commit_count"], "date", pl.Date),
        (get_top_committers, ["name", "commit_count"], "name", pl.String),
    ],
)
def test_empty_dataset_handling(
    func: Callable[[list[dict[str, object]]], pl.DataFrame],
    expected_columns: list[str],
    schema_col: str,
    schema_type: pl.DataType,
) -> None:
    df = func([])

    assert isinstance(df, pl.DataFrame)
    assert len(df) == 0
    assert df.columns == expected_columns
    assert df.schema[schema_col] == schema_type


def test_validation_error_on_malformed_data() -> None:
    # Missing date
    raw_data: list[dict[str, object]] = [{"commit": {"author": {"name": "Alice"}}}]

    with pytest.raises(ValidationError):
        aggregate_commits_by_date(raw_data)

    with pytest.raises(ValidationError):
        get_top_committers(raw_data)

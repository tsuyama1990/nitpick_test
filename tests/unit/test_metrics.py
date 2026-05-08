from datetime import date

import polars as pl

from src.metrics import MetricsTransformer


def test_metrics_transformer() -> None:
    t = MetricsTransformer()
    df_empty = t.process_commits([])
    assert df_empty.is_empty()
    assert t.aggregate_commits_by_date(df_empty).is_empty()
    assert t.get_top_committers(df_empty).is_empty()

    raw = [
        {"name": "A", "date": "2023-01-01T00:00:00Z"},
        {"name": "A", "date": "2023-01-01T01:00:00Z"},
        {"name": "B", "date": "2023-01-02T00:00:00Z"},
    ]
    df = t.process_commits(raw)
    assert df.shape == (3, 2)

    agg_date = t.aggregate_commits_by_date(df)
    assert agg_date.filter(pl.col("date") == date(2023, 1, 1))["commits_count"][0] == 2

    top = t.get_top_committers(df)
    assert top.row(0) == ("A", 2)

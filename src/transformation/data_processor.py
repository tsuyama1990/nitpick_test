import polars as pl

from src.transformation.exceptions import TransformationError


class DataProcessor:
    @staticmethod
    def commits_per_day(df: pl.DataFrame) -> pl.DataFrame:
        """Aggregates commit history to calculate commits per day."""
        if not df.is_empty() and "author_date" not in df.columns:
            msg = "Missing required column: author_date"
            raise TransformationError(msg)
        if df.is_empty():
            return pl.DataFrame(
                {"date": [], "commits": []}, schema={"date": pl.Date, "commits": pl.UInt32}
            )

        return (
            df.with_columns(
                pl.col("author_date")
                .str.to_datetime(format="%Y-%m-%dT%H:%M:%SZ")
                .dt.date()
                .alias("date")
            )
            .group_by("date")
            .agg(pl.len().alias("commits"))
            .sort("date")
        )

    @staticmethod
    def top_committers(df: pl.DataFrame, limit: int = 5) -> pl.DataFrame:
        """Extracts the top N committers by commit count."""
        if not df.is_empty() and "author_name" not in df.columns:
            msg = "Missing required column: author_name"
            raise TransformationError(msg)
        if df.is_empty():
            return pl.DataFrame(
                {"author_name": [], "commits": []},
                schema={"author_name": pl.Utf8, "commits": pl.UInt32},
            )

        return (
            df.group_by("author_name")
            .agg(pl.len().alias("commits"))
            .sort("commits", descending=True)
            .head(limit)
        )

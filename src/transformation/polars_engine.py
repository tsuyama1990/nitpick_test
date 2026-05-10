import polars as pl

from src.domain_models.github import CommitInfo


class PolarsEngine:
    """Handles data transformation using Polars."""

    @staticmethod
    def _to_dataframe(commits: list[CommitInfo]) -> pl.DataFrame:
        """Converts a list of CommitInfo objects into a Polars DataFrame."""
        if not commits:
            return pl.DataFrame(schema={"date": pl.Date, "name": pl.String})

        data = [
            {"date": commit.commit.committer.date.date(), "name": commit.commit.committer.name}
            for commit in commits
        ]

        # Explicitly declare schema to prevent casting errors
        return pl.DataFrame(data, schema={"date": pl.Date, "name": pl.String})

    @staticmethod
    def aggregate_commits_by_date(commits: list[CommitInfo]) -> pl.DataFrame:
        """Aggregates commit counts by date."""
        df = PolarsEngine._to_dataframe(commits)
        if df.is_empty():
            return pl.DataFrame(schema={"date": pl.Date, "commit_count": pl.UInt32})

        return df.group_by("date").agg(pl.len().alias("commit_count")).sort("date")

    @staticmethod
    def get_top_committers(commits: list[CommitInfo], limit: int = 5) -> pl.DataFrame:
        """Aggregates commit counts by committer and returns the top committers."""
        df = PolarsEngine._to_dataframe(commits)
        if df.is_empty():
            return pl.DataFrame(schema={"name": pl.String, "commit_count": pl.UInt32})

        return (
            df.group_by("name")
            .agg(pl.len().alias("commit_count"))
            .sort(["commit_count", "name"], descending=[True, False])
            .head(limit)
        )

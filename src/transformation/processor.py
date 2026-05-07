import polars as pl

from src.domain_models import Commit


class DataTransformer:
    def process_commits(self, commits: list[Commit]) -> tuple[pl.DataFrame, pl.DataFrame]:
        """
        Takes a list of Commit objects and returns:
        1. Commits by Date (YYYY-MM-DD, commit_count)
        2. Top 5 Committers (name, commit_count)
        """
        if not commits:
            empty_date = pl.DataFrame(
                {"date": [], "commit_count": []},
                schema={"date": pl.String, "commit_count": pl.UInt32},
            )
            empty_user = pl.DataFrame(
                {"name": [], "commit_count": []},
                schema={"name": pl.String, "commit_count": pl.UInt32},
            )
            return empty_date, empty_user

        # Convert Pydantic objects to dicts for Polars
        data = []
        for c in commits:
            data.append(
                {"sha": c.sha, "name": c.commit.committer.name, "date": c.commit.committer.date}
            )

        df = pl.DataFrame(data)

        # 1. Date aggregation (YYYY-MM-DD)
        df_date = df.with_columns(pl.col("date").dt.date().cast(pl.String).alias("date_str"))

        commits_by_date = (
            df_date.group_by("date_str")
            .agg(pl.len().alias("commit_count"))
            .sort("date_str")
            .rename({"date_str": "date"})
        )

        # 2. Top committers aggregation
        top_committers = (
            df.group_by("name")
            .agg(pl.len().alias("commit_count"))
            .sort("commit_count", descending=True)
            .head(5)
        )

        return commits_by_date, top_committers

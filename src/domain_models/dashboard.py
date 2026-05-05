import polars as pl
from pydantic import BaseModel, ConfigDict

from src.domain_models.github import RepoMetadata


class DashboardData(BaseModel):
    """
    Data Transfer Object holding all the processed data required by the UI.
    Uses arbitrary_types_allowed to allow Polars DataFrames.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    repo_metadata: RepoMetadata
    daily_commits_df: pl.DataFrame
    top_committers_df: pl.DataFrame

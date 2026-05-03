from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RepositoryMetadata(BaseModel):
    owner: str
    name: str
    star_count: int = Field(ge=0)
    fork_count: int = Field(ge=0)
    open_issue_count: int = Field(ge=0)

    model_config = ConfigDict(extra="forbid")


class CommitRecord(BaseModel):
    commit_hash: str
    author: str
    date: datetime

    model_config = ConfigDict(extra="forbid")


class DashboardData(BaseModel):
    repo_metadata: RepositoryMetadata
    daily_commits_df: Any  # Polars DataFrame
    top_committers_df: Any  # Polars DataFrame

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

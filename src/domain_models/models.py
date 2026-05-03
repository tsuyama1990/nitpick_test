from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RepositoryMetadata(BaseModel):
    """Represents core metadata for a GitHub repository."""

    model_config = ConfigDict(extra="forbid")

    owner: str = Field(min_length=1)
    repo_name: str = Field(min_length=1)
    star_count: int = Field(ge=0)
    fork_count: int = Field(ge=0)
    open_issue_count: int = Field(ge=0)


class CommitRecord(BaseModel):
    """Represents a single commit record."""

    model_config = ConfigDict(extra="forbid")

    commit_hash: str = Field(min_length=1)
    author_name: str = Field(min_length=1)
    timestamp: datetime

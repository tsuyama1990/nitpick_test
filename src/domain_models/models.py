from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class RepositoryMetadata(BaseModel):
    """Precisely represents the core, essential high-level information of a specific target repository."""

    model_config = ConfigDict(extra="forbid")

    owner: str
    repo: str
    star_count: int = Field(ge=0)
    fork_count: int = Field(ge=0)
    open_issue_count: int = Field(ge=0)


class CommitRecord(BaseModel):
    """Precisely represents a single, individual atomic commit within the repository's chronological history."""

    model_config = ConfigDict(extra="forbid")

    commit_hash: str
    author_name: str
    timestamp: datetime | date

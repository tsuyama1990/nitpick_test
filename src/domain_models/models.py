from datetime import datetime

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

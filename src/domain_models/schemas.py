from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RepositoryMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stargazers_count: int = Field(ge=0)
    forks_count: int = Field(ge=0)
    open_issues_count: int = Field(ge=0)


class CommitAuthor(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    date: datetime


class CommitInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    author: CommitAuthor
    message: str


class Commit(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sha: str
    commit: CommitInfo

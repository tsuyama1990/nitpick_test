from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RepositoryMetrics(BaseModel):
    stargazers_count: int
    forks_count: int
    open_issues_count: int

    model_config = ConfigDict(extra="forbid")


class CommitAuthor(BaseModel):
    name: str
    date: datetime

    model_config = ConfigDict(extra="forbid")


class CommitData(BaseModel):
    author: CommitAuthor

    model_config = ConfigDict(extra="forbid")


class CommitItem(BaseModel):
    commit: CommitData

    model_config = ConfigDict(extra="forbid")

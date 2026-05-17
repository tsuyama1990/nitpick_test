import datetime

from pydantic import BaseModel, ConfigDict


class RepositoryMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stargazers_count: int
    forks_count: int
    open_issues_count: int


class CommitAuthor(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    date: datetime.datetime


class CommitData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    author: CommitAuthor


class CommitItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    commit: CommitData

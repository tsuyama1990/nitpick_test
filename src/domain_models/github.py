from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class Repository(BaseModel):
    model_config = ConfigDict(extra="ignore")

    stargazers_count: int = Field(ge=0)
    forks_count: int = Field(ge=0)
    open_issues_count: int = Field(ge=0)


class Committer(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str = Field(min_length=1)
    date: datetime


class CommitInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")

    committer: Committer


class Commit(BaseModel):
    model_config = ConfigDict(extra="ignore")

    sha: str = Field(min_length=1)
    commit: CommitInfo

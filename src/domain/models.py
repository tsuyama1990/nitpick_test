from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class RepositoryMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    owner: str
    stargazers_count: int = Field(ge=0)
    forks_count: int = Field(ge=0)
    open_issues_count: int = Field(ge=0)


class CommitRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sha: str
    author_name: str
    date: datetime | date

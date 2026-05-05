from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class RepositoryMetadata(BaseModel):
    owner: str
    name: str
    stargazers_count: int = Field(ge=0)
    forks_count: int = Field(ge=0)
    open_issues_count: int = Field(ge=0)

    model_config = ConfigDict(extra="ignore")


class CommitRecord(BaseModel):
    sha: str
    author: str
    date: datetime | date

    model_config = ConfigDict(extra="ignore")

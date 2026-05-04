from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RepositoryMetadata(BaseModel):
    model_config = ConfigDict(extra="ignore")

    owner: str
    name: str
    stars: int = Field(ge=0, alias="stargazers_count")
    forks: int = Field(ge=0, alias="forks_count")
    open_issues: int = Field(ge=0, alias="open_issues_count")


class CommitRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    hash: str = Field(alias="sha")
    author: str
    date: datetime

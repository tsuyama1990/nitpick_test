from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class RepositoryMetadata(BaseModel):
    owner: str = Field(alias="owner")
    name: str = Field(alias="name")
    stargazers_count: int = Field(ge=0, alias="stargazers_count")
    forks_count: int = Field(ge=0, alias="forks_count")
    open_issues_count: int = Field(ge=0, alias="open_issues_count")

    model_config = ConfigDict(extra="ignore")


class CommitRecord(BaseModel):
    sha: str = Field(alias="sha")
    author: str = Field(alias="author")
    date: datetime | date

    model_config = ConfigDict(extra="ignore")

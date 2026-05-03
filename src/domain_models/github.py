from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RepositoryMetadata(BaseModel):
    owner: str
    repo: str
    stargazers_count: int = Field(ge=0)
    forks_count: int = Field(ge=0)
    open_issues_count: int = Field(ge=0)

    model_config = ConfigDict(extra="forbid")


class CommitRecord(BaseModel):
    sha: str = Field(min_length=1)
    author_name: str
    date: datetime

    model_config = ConfigDict(extra="forbid")

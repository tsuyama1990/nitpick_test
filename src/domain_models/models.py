from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RepositoryMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    owner: str
    name: str
    stars: int = Field(ge=0)
    forks: int = Field(ge=0)
    open_issues: int = Field(ge=0)


class CommitRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    hash: str
    author: str
    date: datetime

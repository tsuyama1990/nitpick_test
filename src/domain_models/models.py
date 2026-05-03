from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RepositoryMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    owner: str = Field(..., description="The owner of the repository")
    repo: str = Field(..., description="The name of the repository")
    stars: int = Field(..., ge=0, description="The number of stars")
    forks: int = Field(..., ge=0, description="The number of forks")
    open_issues: int = Field(..., ge=0, description="The number of open issues")


class CommitRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    commit_hash: str = Field(..., description="The hash of the commit")
    author_name: str = Field(..., description="The name of the author")
    timestamp: datetime = Field(..., description="The timestamp of the commit")

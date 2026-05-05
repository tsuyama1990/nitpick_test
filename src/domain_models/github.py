from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RepoMetadata(BaseModel):
    """Pydantic model representing repository metadata."""

    model_config = ConfigDict(extra="forbid")

    stargazers_count: int = Field(ge=0, description="Total number of stars")
    forks_count: int = Field(ge=0, description="Total number of forks")
    open_issues_count: int = Field(ge=0, description="Total number of open issues")


class CommitRecord(BaseModel):
    """Pydantic model representing a single commit record."""

    model_config = ConfigDict(extra="forbid")

    date: datetime = Field(description="Date and time of the commit")
    author_name: str = Field(min_length=1, description="Name of the commit author")
    message: str = Field(description="Commit message")

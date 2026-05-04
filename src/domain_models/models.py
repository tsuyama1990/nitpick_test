from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RepositoryMetadata(BaseModel):
    """Precisely represents the core essential information of a target repository."""

    model_config = ConfigDict(extra="forbid")

    owner: str = Field(..., description="The owner of the repository.")
    name: str = Field(..., description="The name of the repository.")
    stargazers_count: int = Field(..., ge=0, description="The number of stars.")
    forks_count: int = Field(..., ge=0, description="The number of forks.")
    open_issues_count: int = Field(..., ge=0, description="The number of open issues.")


class CommitRecord(BaseModel):
    """Precisely represents a single individual atomic commit within the repository's chronological history."""

    model_config = ConfigDict(extra="forbid")

    sha: str = Field(..., description="The commit hash.")
    author_name: str = Field(..., description="The name of the author.")
    date: datetime = Field(..., description="The timestamp of the commit.")

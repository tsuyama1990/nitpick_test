from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RepositoryMetadata(BaseModel):
    """
    Core metadata of a GitHub repository.
    """

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., description="Name of the repository (e.g. 'streamlit')")
    owner: str = Field(..., description="Owner of the repository (e.g. 'streamlit')")
    stargazers_count: int = Field(..., ge=0, description="Number of stars")
    forks_count: int = Field(..., ge=0, description="Number of forks")
    open_issues_count: int = Field(..., ge=0, description="Number of open issues")


class CommitRecord(BaseModel):
    """
    A single commit in the repository's history.
    """

    model_config = ConfigDict(extra="forbid")

    sha: str = Field(..., min_length=1, description="Commit hash")
    author_name: str = Field(..., min_length=1, description="Name of the author")
    date: datetime = Field(..., description="Timestamp of the commit")

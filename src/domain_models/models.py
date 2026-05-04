from datetime import datetime

from pydantic import AliasPath, BaseModel, ConfigDict, Field


class RepositoryMetadata(BaseModel):
    """Metadata representing a target GitHub repository."""

    owner: str = Field(validation_alias=AliasPath("owner", "login"), default="")
    name: str
    stargazers_count: int = Field(ge=0)
    forks_count: int = Field(ge=0)
    open_issues_count: int = Field(ge=0)

    model_config = ConfigDict(extra="ignore", populate_by_name=True)


class CommitRecord(BaseModel):
    """An atomic commit in a repository's history."""

    sha: str
    author_name: str = Field(validation_alias=AliasPath("commit", "author", "name"))
    timestamp: datetime = Field(validation_alias=AliasPath("commit", "author", "date"))

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

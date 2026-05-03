from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class Owner(BaseModel):
    model_config = ConfigDict(extra="ignore")
    login: str


class RepositoryMetadata(BaseModel):
    """Represents core metadata of a GitHub repository."""

    model_config = ConfigDict(extra="forbid")

    owner_obj: Owner = Field(..., description="The owner object of the repository.", alias="owner")
    repo_name: str = Field(..., description="The name of the repository.", alias="name")
    star_count: int = Field(..., ge=0, description="The number of stars.", alias="stargazers_count")
    fork_count: int = Field(..., ge=0, description="The number of forks.", alias="forks_count")
    open_issue_count: int = Field(..., ge=0, description="The number of open issues.", alias="open_issues_count")

    @property
    def owner(self) -> str:
        return self.owner_obj.login


class CommitAuthor(BaseModel):
    model_config = ConfigDict(extra="ignore")
    name: str = Field(..., description="The author's name.")
    date: datetime = Field(..., description="The date of the commit.")


class CommitDetails(BaseModel):
    model_config = ConfigDict(extra="ignore")
    author: CommitAuthor


class CommitRecord(BaseModel):
    """Represents a single commit record."""

    model_config = ConfigDict(extra="forbid")

    sha: str = Field(..., description="The commit hash.")
    commit: CommitDetails

    @property
    def author_name(self) -> str:
        return self.commit.author.name

    @property
    def date(self) -> datetime:
        return self.commit.author.date

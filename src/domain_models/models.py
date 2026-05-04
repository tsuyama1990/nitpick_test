from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RepositoryMetadata(BaseModel):
    owner: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    star_count: int = Field(..., ge=0, alias="stargazers_count")
    fork_count: int = Field(..., ge=0, alias="forks_count")
    open_issue_count: int = Field(..., ge=0, alias="open_issues_count")

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class CommitAuthor(BaseModel):
    name: str = Field(..., min_length=1)
    date: datetime

    model_config = ConfigDict(extra="forbid")


class CommitDetail(BaseModel):
    author: CommitAuthor

    model_config = ConfigDict(extra="forbid")


class CommitRecord(BaseModel):
    sha: str = Field(..., min_length=1)
    commit: CommitDetail

    model_config = ConfigDict(extra="forbid")

    @property
    def author_name(self) -> str:
        return self.commit.author.name

    @property
    def timestamp(self) -> datetime:
        return self.commit.author.date

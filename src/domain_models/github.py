from pydantic import BaseModel, ConfigDict, Field


class RepositoryInfo(BaseModel):
    stargazers_count: int = Field(alias="stargazers_count")
    forks_count: int = Field(alias="forks_count")
    open_issues_count: int = Field(alias="open_issues_count")

    model_config = ConfigDict(extra="ignore")


class CommitAuthor(BaseModel):
    name: str
    date: str

    model_config = ConfigDict(extra="ignore")


class CommitDetail(BaseModel):
    author: CommitAuthor

    model_config = ConfigDict(extra="ignore")


class CommitInfo(BaseModel):
    commit: CommitDetail

    model_config = ConfigDict(extra="ignore")
